# Mobile Catalog And Service Cap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Match the public mobile catalog layout to the approved dual-column reference while showing up to five enabled services per game and enforcing the five-enabled-service limit.

**Architecture:** The backend `GameCatalog` remains the enforcement seam for enabled-service capacity, returning a domain error that the existing HTTP adapter maps to a `409` response. Alembic backfills the four seeded games, while seed data keeps fresh databases consistent. The frontend changes only the public catalog presentation at responsive breakpoints and keeps `SiteSetting.studio_image` as the single brand-image source.

**Tech Stack:** FastAPI, SQLAlchemy 2, Alembic, PostgreSQL/SQLite, Next.js 15, React 19, TypeScript, CSS Modules, Vitest, pytest.

**Spec:** `.scratch/11hao-esports/issues/001-esports-management-system-spec.md`

## Global Constraints

- Use `Game`, `GameService`, and `SiteSetting` terminology from `CONTEXT.md`.
- Preserve disabled GameService records; the limit is five enabled services per Game.
- Return structured API errors with `code`, `message`, and `details`.
- Keep `frontend/public/images/studio.jpg` as the canonical bundled copy of `图片/工作室图标.jpg`.
- Public desktop layout remains unchanged; at `375px–600px` use the approved left-list/right-demand two-column layout, and below `375px` stack the columns.
- Do not overwrite administrator-edited game or service data in the migration.

---

### Task 1: Enforce Enabled Service Capacity

**Files:**
- Modify: `backend/app/game_catalog.py:12-29,110-137`
- Modify: `backend/app/main.py:79-88`
- Modify: `backend/tests/test_game_catalog.py`
- Modify: `backend/tests/test_public_games.py`

**Interfaces:**
- Consumes: `GameCatalog.create_service(game_id: int, payload: ServiceWrite) -> GameService`
- Produces: `EnabledServiceLimitReached(GameCatalogError)` and HTTP `409` body `{ "code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求", "details": {} }`.

- [ ] **Step 1: Write the failing catalog test**

```python
def test_create_service_rejects_a_sixth_enabled_service(db: Session):
    game = GameCatalog(db).list_admin_games()[0]
    for index in range(2):
        GameCatalog(db).create_service(game.id, ServiceWrite(
            name=f"补充需求 {index}", price="¥ 1", description="测试", sort_order=10 + index, is_active=True,
        ))

    with pytest.raises(EnabledServiceLimitReached):
        GameCatalog(db).create_service(game.id, ServiceWrite(
            name="第六项", price="¥ 1", description="测试", sort_order=99, is_active=True,
        ))
```

- [ ] **Step 2: Run the catalog test to verify it fails**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest tests/test_game_catalog.py -k sixth_enabled -v`

Expected: FAIL because no capacity error exists.

- [ ] **Step 3: Write the failing HTTP test**

```python
def test_admin_receives_conflict_for_a_sixth_enabled_service(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "admin-password"})
    game = client.get("/api/admin/games").json()[0]
    for index in range(2):
        client.post(f"/api/admin/games/{game['id']}/services", json={
            "name": f"补充需求 {index}", "price": "¥ 1", "description": "测试", "sort_order": 10 + index, "is_active": True,
        })

    response = client.post(f"/api/admin/games/{game['id']}/services", json={
        "name": "第六项", "price": "¥ 1", "description": "测试", "sort_order": 99, "is_active": True,
    })

    assert response.status_code == 409
    assert response.json() == {"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求", "details": {}}
```

- [ ] **Step 4: Run the HTTP test to verify it fails**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest tests/test_public_games.py -k sixth_enabled -v`

Expected: FAIL because the endpoint creates a sixth enabled GameService.

- [ ] **Step 5: Implement the minimal catalog and HTTP mapping**

```python
class EnabledServiceLimitReached(GameCatalogError):
    pass

def create_service(self, game_id: int, payload: ServiceWrite) -> GameService:
    game = self.db.get(Game, game_id)
    if not game:
        raise GameNotFound()
    enabled_count = self.db.scalar(
        select(func.count()).select_from(GameService).where(
            GameService.game_id == game_id,
            GameService.is_active.is_(True),
        )
    )
    if payload.is_active and enabled_count >= 5:
        raise EnabledServiceLimitReached()
```

Map `EnabledServiceLimitReached` in `catalog_http_error` to `HTTPException(409, detail={"code": "SERVICE_LIMIT_REACHED", "message": "每个游戏最多 5 个启用需求"})`.

- [ ] **Step 6: Prevent edits from enabling a sixth service**

```python
def update_service(self, service_id: int, payload: ServiceWrite) -> GameService:
    service = self.db.get(GameService, service_id)
    if not service:
        raise ServiceNotFound()
    if payload.is_active and not service.is_active:
        enabled_count = self.db.scalar(
            select(func.count()).select_from(GameService).where(
                GameService.game_id == service.game_id,
                GameService.is_active.is_(True),
            )
        )
        if enabled_count >= 5:
            raise EnabledServiceLimitReached()
```

Apply the same check in `set_service_enabled` only when `enabled=True` and the service is currently disabled.

- [ ] **Step 7: Run focused tests to verify they pass**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest tests/test_game_catalog.py tests/test_public_games.py -k "sixth_enabled or service" -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/app/game_catalog.py backend/app/main.py backend/tests/test_game_catalog.py backend/tests/test_public_games.py
```

### Task 2: Backfill And Seed Five Editable Services

**Files:**
- Modify: `backend/app/seed.py:6-20`
- Create: `backend/alembic/versions/0003_backfill_seed_services.py`
- Test: `backend/tests/test_public_games.py`

**Interfaces:**
- Consumes: the four stable Game slugs in `SEED_GAMES`.
- Produces: fresh databases with five enabled services per seeded Game and existing databases with only missing default services inserted.

- [ ] **Step 1: Write the failing seed expectation**

```python
def test_seeded_games_have_five_enabled_services(client):
    games = client.get("/api/games").json()

    assert len(games) == 4
    assert all(len(game["services"]) == 5 for game in games)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest tests/test_public_games.py -k seeded_games_have_five -v`

Expected: FAIL because every seed currently has three services.

- [ ] **Step 3: Expand seed definitions to five services**

```python
SEED_GAMES = [
    ("原神", ..., [("日常委托", "¥ 30"), ("深渊满星", "¥ 88"), ("角色培养", "¥ 120"), ("提瓦特探索", "¥ 30"), ("养成目标", "¥ 120")]),
    ("崩坏·星穹铁道", ..., [("日常任务", "¥ 25"), ("混沌回忆", "¥ 80"), ("角色培养", "¥ 100"), ("版本内容", "¥ 25"), ("银河冒险", "¥ 100")]),
    ("绝区零", ..., [("每日活跃", "¥ 20"), ("零号空洞", "¥ 60"), ("代理人培养", "¥ 100"), ("都市幻想", "¥ 20"), ("角色养成", "¥ 100")]),
    ("鸣潮", ..., [("每日任务", "¥ 25"), ("无音区材料", "¥ 50"), ("角色培养", "¥ 120"), ("账号养成", "¥ 120"), ("动作冒险", "¥ 25")]),
]
```

- [ ] **Step 4: Add an idempotent data migration**

```python
def upgrade() -> None:
    games = sa.table("games", sa.column("id", sa.Integer), sa.column("slug", sa.String))
    services = sa.table(
        "game_services",
        sa.column("game_id", sa.Integer), sa.column("name", sa.String), sa.column("price", sa.String),
        sa.column("description", sa.String), sa.column("sort_order", sa.Integer), sa.column("is_active", sa.Boolean),
    )
    connection = op.get_bind()
    for slug, additions in BACKFILL.items():
        game_id = connection.execute(sa.select(games.c.id).where(games.c.slug == slug)).scalar_one_or_none()
        if game_id is None:
            continue
        existing_names = set(connection.execute(sa.select(services.c.name).where(services.c.game_id == game_id)).scalars())
        for sort_order, (name, price) in enumerate(additions, start=3):
            if name not in existing_names:
                connection.execute(services.insert().values(game_id=game_id, name=name, price=price, description="按需求提供专业服务", sort_order=sort_order, is_active=True))
```

Use the migration revision after `0002_admin_users`; leave `downgrade()` empty because default service content is business data and must not be destroyed.

- [ ] **Step 5: Run the focused test to verify it passes**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest tests/test_public_games.py -k seeded_games_have_five -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/seed.py backend/alembic/versions/0003_backfill_seed_services.py backend/tests/test_public_games.py
```

### Task 3: Show Full Catalog And Five Public Service Cards

**Files:**
- Modify: `frontend/app/admin/page.tsx:46-49`
- Modify: `frontend/components/public-home.tsx:147-149`
- Modify: `frontend/tests/home.test.ts`

**Interfaces:**
- Consumes: `Game.services` already filtered to enabled records by the public API.
- Produces: the dashboard renders all games and the public demand list renders at most five enabled services.

- [ ] **Step 1: Write the failing presentation helper tests**

Export a pure `featuredServices` helper from `public-home.tsx` or move it to `frontend/lib/public-home.ts`:

```ts
it("limits public demand cards to five enabled services", () => {
  const services = Array.from({ length: 6 }, (_, index) => ({ id: index + 1, is_active: true }));

  expect(featuredServices(services)).toHaveLength(5);
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `npm test -- --run tests/home.test.ts`

Expected: FAIL because the current component slices to three entries and exports no helper.

- [ ] **Step 3: Implement the minimal presentation change**

```ts
export function featuredServices<T>(services: T[]): T[] {
  return services.slice(0, 5);
}
```

Replace `services.slice(0, 3)` with `featuredServices(services)`. Replace `games.slice(0, 4)` in the dashboard table with `games`.

- [ ] **Step 4: Run the frontend tests to verify they pass**

Run: `npm test -- --run tests/home.test.ts`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/app/admin/page.tsx frontend/components/public-home.tsx frontend/tests/home.test.ts
```

### Task 4: Apply Approved Mobile Catalog Layout And Default Brand Image

**Files:**
- Modify: `frontend/components/public-home.module.css:597-692`
- Modify: `frontend/components/public-home.tsx:35,147-149`
- Modify: `frontend/tests/home.test.ts`

**Interfaces:**
- Consumes: `settings.studio_image` with `/images/studio.jpg` as fallback.
- Produces: the same studio image in header, hero emblem, and footer; a dual-column mobile catalog for widths `375px–600px`.

- [ ] **Step 1: Write the failing brand-image source test**

```ts
it("uses the bundled tiger logo as the public brand fallback", () => {
  const source = readFileSync(resolve(process.cwd(), "components/public-home.tsx"), "utf8");

  expect(source).toContain('const STUDIO_IMAGE = "/images/studio.jpg"');
  expect((source.match(/src=\{studioImage\}/g) ?? []).length).toBe(3);
});
```

- [ ] **Step 2: Run it to verify it fails only if the three shared sources regress**

Run: `npm test -- --run tests/home.test.ts`

Expected: PASS after confirming the existing shared source; this is a regression guard, not a new behavior failure.

- [ ] **Step 3: Replace mobile breakpoint rules**

At `max-width: 600px`, keep `.workspace` as a two-column grid:

```css
.workspace {
  grid-template-columns: minmax(150px, 0.76fr) minmax(0, 1.24fr);
  gap: 14px;
}

.gameButton { min-height: 68px; padding: 10px; }
.gameButton img { width: 42px; height: 42px; }
.demandCard { grid-template-columns: 40px minmax(0, 1fr); padding: 14px; }
```

At `max-width: 374px`, set `.workspace { grid-template-columns: 1fr; }`. Keep hero and footer compact, preserve readable 12px minimum body text, and do not alter desktop rules.

- [ ] **Step 4: Run typecheck and production build**

Run: `npm run typecheck; npm run build`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/components/public-home.module.css frontend/components/public-home.tsx frontend/tests/home.test.ts
```

### Task 5: Full Verification And Docker Data Migration

**Files:**
- Modify: no source files expected.

**Interfaces:**
- Consumes: completed Tasks 1-4.
- Produces: verified local tests, production build, migrated Docker PostgreSQL data, and a live five-service public catalog.

- [ ] **Step 1: Run all backend tests**

Run: `conda run -n copy_page_and_Backend_Management_System python -m pytest`

Expected: PASS with no failures.

- [ ] **Step 2: Run all frontend checks**

Run: `npm test; npm run typecheck; npm run build`

Expected: PASS with no failures.

- [ ] **Step 3: Rebuild Docker and apply Alembic migration**

Run: `docker compose up -d --build`

Expected: backend logs include an Alembic upgrade to the new revision; `docker compose ps` shows healthy db/backend and running frontend.

- [ ] **Step 4: Verify persisted data through public API**

Run:

```powershell
$games = Invoke-RestMethod http://localhost:3000/api/games
$games | ForEach-Object { "$($_.name): $($_.services.Count)" }
```

Expected: each seeded game reports `5`; existing non-seed games are unchanged.

- [ ] **Step 5: Verify service-cap error through authenticated API**

Run the HTTP test from Task 1 against the Docker stack or verify the admin UI displays `每个游戏最多 5 个启用需求` after attempting a sixth enabled service.

- [ ] **Step 6: Commit verification-only changes if any**

```bash
git status --short
```

Expected: no generated files are staged; do not commit Docker volumes, `.env`, or caches.

## Self-Review

- Spec coverage: service creation/editing/enabling capacity is covered in Task 1; fresh and existing data in Task 2; dashboard and public five-item visibility in Task 3; the approved responsive layout and three shared brand images in Task 4; Docker migration and live verification in Task 5.
- No placeholders: all tasks list exact files, seams, commands, and expected outcomes.
- Type consistency: `EnabledServiceLimitReached`, `featuredServices`, and `redirectIfUnauthorized` are not reused under alternate names.
