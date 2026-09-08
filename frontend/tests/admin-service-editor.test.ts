import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("admin service editing", () => {
  it("maintains approved GameService fields and surfaces service-cap conflicts", () => {
    const source = readFileSync(resolve(process.cwd(), "app/admin/games/[id]/page.tsx"), "utf8");

    expect(source).toContain('price: ""');
    expect(source).not.toContain("<span>参考价格</span>");
    expect(source).toContain("sort_order");
    expect(source).toContain("toggleService");
    expect(source).toContain('body?.code === "SERVICE_LIMIT_REACHED"');
    expect(source).not.toContain(["service", "items"].join("-"));
    expect(source).not.toContain(["child", "project"].join("-"));
  });

  it("omits direct service prices from the admin services list", () => {
    const source = readFileSync(resolve(process.cwd(), "app/admin/services/page.tsx"), "utf8");

    expect(source).not.toContain("<th>参考价格</th>");
    expect(source).not.toContain("{service.price}");
    expect(source).not.toContain(["子", "项目"].join(""));
  });

  it("manages child services without per-child images inside the game editor", () => {
    const source = readFileSync(resolve(process.cwd(), "app/admin/games/[id]/page.tsx"), "utf8");

    expect(source).toContain("type ChildService");
    expect(source).toContain("child_services: ChildService[]");
    expect(source).toContain("childServicePayload");
    expect(source).toContain("/api/admin/services/${service.id}/child-services");
    expect(source).toContain("/api/admin/child-services/${childService.id}");
    expect(source).toContain("method: \"DELETE\"");
    expect(source).toContain("child-services/reorder");
    expect(source).toContain("保存子服务");
    expect(source).toContain("image_path: null");
    expect(source).toContain("const file = event.target.files?.[0]");
    expect(source).not.toContain("清空配图");
    expect(source).not.toContain("子服务配图");
    expect(source).not.toContain("chooseChildServiceImage");
    expect(source).not.toContain("chooseNewChildServiceImage");
    expect(source).not.toContain(["child", "project"].join("-"));
    expect(source).not.toContain(["子", "项目"].join(""));
  });
});
