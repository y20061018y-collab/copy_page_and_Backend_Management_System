"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AdminLayout, AdminPageTitle } from "../../../../components/admin-layout";
import { uploadErrorMessage } from "../../../../lib/upload-error";

type ChildService = { id: number; name: string; price: string; description: string; sort_order: number };
type ChildServiceDraft = Omit<ChildService, "id">;
type Service = { id: number; name: string; price: string; description: string; cover_image: string; sort_order: number; is_active: boolean; child_services: ChildService[] };
type Game = { id: number; name: string; slug: string; tag: string; description: string; cover_image: string; accent_color: string; accent_color_2: string; sort_order: number; is_active: boolean; services: Service[] };

const emptyService = { name: "", price: "", description: "", sort_order: 0, is_active: true };
const emptyChildService: ChildServiceDraft = { name: "", price: "", description: "", sort_order: 0 };

const gamePayload = (game: Game) => ({
  name: game.name,
  slug: game.slug,
  tag: game.tag,
  description: game.description,
  cover_image: game.cover_image,
  accent_color: game.accent_color,
  accent_color_2: game.accent_color_2,
  sort_order: game.sort_order,
  is_active: game.is_active,
});

const servicePayload = (service: Service) => ({
  name: service.name,
  price: "",
  description: service.description,
  cover_image: service.cover_image,
  sort_order: service.sort_order,
  is_active: service.is_active,
});

const childServicePayload = (childService: ChildServiceDraft) => ({
  name: childService.name,
  price: childService.price,
  description: childService.description,
  image_path: null,
  sort_order: childService.sort_order,
});

async function responseMessage(response: Response, fallback: string) {
  if (fallback.includes("图片上传")) return uploadErrorMessage(response, fallback);
  const body = await response.json().catch(() => null);
  if (body?.code === "SERVICE_LIMIT_REACHED") return body.message;
  if (body?.message) return body.message;
  return fallback;
}

export default function EditGame() {
  const { id } = useParams<{ id: string }>();
  const [game, setGame] = useState<Game | null>(null);
  const [newService, setNewService] = useState(emptyService);
  const [newChildServices, setNewChildServices] = useState<Record<number, ChildServiceDraft>>({});
  const [pendingCoverFile, setPendingCoverFile] = useState<File | null>(null);
  const [coverPreview, setCoverPreview] = useState("");
  const [message, setMessage] = useState("");

  const load = () => fetch("/api/admin/games")
    .then((response) => response.ok ? response.json() : [])
    .then((items: Game[]) => {
      const next = items.find((item) => String(item.id) === id) ?? null;
      if (next) {
        next.services.sort((a, b) => a.sort_order - b.sort_order || a.id - b.id);
        next.services.forEach((service) => {
          service.child_services = [...(service.child_services ?? [])].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id);
        });
        setCoverPreview(next.cover_image);
        setPendingCoverFile(null);
      }
      setGame(next);
    });

  useEffect(() => { void load(); }, [id]);

  const updateGame = <K extends keyof Game>(key: K, value: Game[K]) => game && setGame({ ...game, [key]: value });
  const updateService = <K extends keyof Service>(serviceId: number, key: K, value: Service[K]) => game && setGame({
    ...game,
    services: game.services.map((service) => service.id === serviceId ? { ...service, [key]: value } : service),
  });
  const updateChildService = <K extends keyof ChildService>(serviceId: number, childServiceId: number, key: K, value: ChildService[K]) => game && setGame({
    ...game,
    services: game.services.map((service) => service.id === serviceId ? {
      ...service,
      child_services: service.child_services.map((childService) => childService.id === childServiceId ? { ...childService, [key]: value } : childService),
    } : service),
  });
  const updateNewChildService = <K extends keyof ChildServiceDraft>(serviceId: number, key: K, value: ChildServiceDraft[K]) => setNewChildServices((current) => ({
    ...current,
    [serviceId]: { ...(current[serviceId] ?? emptyChildService), [key]: value },
  }));

  const uploadCover = async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("/api/admin/uploads/game-cover", { method: "POST", body });
    if (!response.ok) throw new Error(await responseMessage(response, "图片上传失败"));
    return (await response.json()).path as string;
  };

  const saveGame = async (event: FormEvent) => {
    event.preventDefault();
    if (!game) return;
    setMessage("保存中...");
    try {
      const coverImage = pendingCoverFile ? await uploadCover(pendingCoverFile) : game.cover_image;
      const response = await fetch(`/api/admin/games/${game.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(gamePayload({ ...game, cover_image: coverImage })),
      });
      if (!response.ok) {
        setMessage(await responseMessage(response, "保存失败，请检查 Slug 是否重复"));
        return;
      }
      setMessage("游戏资料已保存");
      void load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "保存失败");
    }
  };

  const saveService = async (service: Service) => {
    setMessage("保存服务中...");
    const response = await fetch(`/api/admin/services/${service.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(servicePayload(service)),
    });
    setMessage(response.ok ? "服务已保存" : await responseMessage(response, "服务保存失败"));
    if (response.ok) void load();
  };

  const toggleService = async (service: Service) => {
    const response = await fetch(`/api/admin/services/${service.id}/${service.is_active ? "disable" : "enable"}`, { method: "POST" });
    setMessage(response.ok ? "服务状态已更新" : await responseMessage(response, "服务状态更新失败"));
    if (response.ok) void load();
  };

  const moveService = async (index: number, direction: -1 | 1) => {
    if (!game) return;
    const target = index + direction;
    if (target < 0 || target >= game.services.length) return;
    const next = [...game.services];
    [next[index], next[target]] = [next[target], next[index]];
    await fetch(`/api/admin/games/${game.id}/services/reorder`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(next.map((item, position) => ({ id: item.id, sort_order: position }))),
    });
    void load();
  };

  const addService = async (event: FormEvent) => {
    event.preventDefault();
    if (!game) return;
    setMessage("添加服务中...");
    const response = await fetch(`/api/admin/games/${game.id}/services`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newService, cover_image: game.cover_image, sort_order: game.services.length }),
    });
    if (!response.ok) {
      setMessage(await responseMessage(response, "添加失败"));
      return;
    }
    setNewService(emptyService);
    setMessage("服务已添加");
    void load();
  };

  const chooseCover = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !game) return;
    setPendingCoverFile(file);
    setCoverPreview(URL.createObjectURL(file));
    setMessage("已选择新封面，点击保存游戏资料后生效");
  };

  const chooseServiceCover = async (serviceId: number, event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    const service = game?.services.find((item) => item.id === serviceId);
    if (!file || !service) return;
    setMessage("需求封面上传中...");
    try {
      const coverImage = await uploadCover(file);
      const response = await fetch(`/api/admin/services/${serviceId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(servicePayload({ ...service, cover_image: coverImage })),
      });
      if (!response.ok) throw new Error(await responseMessage(response, "需求封面保存失败"));
      updateService(serviceId, "cover_image", (await response.json()).cover_image);
      setMessage("需求封面已上传并保存");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "需求封面上传失败");
    }
  };

  const saveChildService = async (childService: ChildService) => {
    setMessage("保存子服务中...");
    const response = await fetch(`/api/admin/child-services/${childService.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(childServicePayload(childService)),
    });
    setMessage(response.ok ? "子服务已保存" : await responseMessage(response, "子服务保存失败"));
    if (response.ok) void load();
  };

  const deleteChildService = async (childService: ChildService) => {
    if (!confirm(`删除子服务 ${childService.name}？`)) return;
    const response = await fetch(`/api/admin/child-services/${childService.id}`, { method: "DELETE" });
    setMessage(response.ok ? "子服务已删除" : await responseMessage(response, "子服务删除失败"));
    if (response.ok) void load();
  };

  const moveChildService = async (service: Service, index: number, direction: -1 | 1) => {
    const target = index + direction;
    if (target < 0 || target >= service.child_services.length) return;
    const next = [...service.child_services];
    [next[index], next[target]] = [next[target], next[index]];
    await fetch(`/api/admin/services/${service.id}/child-services/reorder`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(next.map((item, position) => ({ id: item.id, sort_order: position }))),
    });
    void load();
  };

  const addChildService = async (service: Service, event: FormEvent) => {
    event.preventDefault();
    const draft = newChildServices[service.id] ?? emptyChildService;
    setMessage("添加子服务中...");
    const response = await fetch(`/api/admin/services/${service.id}/child-services`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(childServicePayload({ ...draft, sort_order: service.child_services.length })),
    });
    if (!response.ok) {
      setMessage(await responseMessage(response, "添加子服务失败"));
      return;
    }
    setNewChildServices((current) => ({ ...current, [service.id]: emptyChildService }));
    setMessage("子服务已添加");
    void load();
  };

  if (!game) return <AdminLayout active="games" crumb="游戏编辑"><p className="admin-v2-loading">正在加载游戏资料...</p></AdminLayout>;

  return <AdminLayout active="games" crumb={`${game.name} · 编辑`}>
    <AdminPageTitle eyebrow="GAME EDITOR" title={game.name} description="游戏资料与服务在此处统一维护，保存后会同步到前台。" actions={<a className="admin-v2-secondary" href="/admin/games">返回目录</a>} />
    <form className="admin-v2-panel admin-v2-form-panel" onSubmit={saveGame}>
      <div className="admin-v2-form-grid">
        <label className="admin-v2-field"><span>游戏名称</span><input value={game.name} onChange={(event) => updateGame("name", event.target.value)} required /></label>
        <label className="admin-v2-field"><span>Slug</span><input value={game.slug} onChange={(event) => updateGame("slug", event.target.value)} required /></label>
        <label className="admin-v2-field"><span>游戏分类</span><input value={game.tag} onChange={(event) => updateGame("tag", event.target.value)} /></label>
        <label className="admin-v2-field"><span>排序值</span><input type="number" value={game.sort_order} onChange={(event) => updateGame("sort_order", Number(event.target.value))} /></label>
        <label className="admin-v2-field is-wide"><span>前台简介</span><textarea value={game.description} onChange={(event) => updateGame("description", event.target.value)} /></label>
        <label className="admin-v2-field"><span>展示状态</span><select value={game.is_active ? "active" : "inactive"} onChange={(event) => updateGame("is_active", event.target.value === "active")}><option value="active">前台展示</option><option value="inactive">暂不展示</option></select></label>
        <label className="admin-v2-field"><span>游戏封面</span><div className="admin-v2-cover"><img src={coverPreview || game.cover_image} alt="游戏封面" /><input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseCover} /></div></label>
      </div>
      <div className="admin-v2-save-line"><button className="admin-v2-primary">保存游戏资料</button><span className="admin-v2-message">{message}</span></div>
    </form>

    <section style={{ marginTop: 28 }}>
      <AdminPageTitle eyebrow="SERVICES" title="服务" description="每个游戏最多展示 5 个启用服务，价格维护在子服务上。" />
      <div className="admin-v2-service-list">{game.services.map((service, index) => {
        const draft = newChildServices[service.id] ?? emptyChildService;

        return <article className={`admin-v2-service-card ${service.is_active ? "" : "is-disabled"}`} key={service.id}>
          <b className="admin-v2-service-index">{String(index + 1).padStart(2, "0")}</b>
          <div className="admin-v2-service-fields">
            <label className="admin-v2-field"><span>服务名称</span><input value={service.name} onChange={(event) => updateService(service.id, "name", event.target.value)} /></label>
            <label className="admin-v2-field"><span>服务说明</span><textarea value={service.description} onChange={(event) => updateService(service.id, "description", event.target.value)} /></label>
            <label className="admin-v2-field"><span>需求封面</span><div className="admin-v2-cover"><img src={service.cover_image} alt={`${service.name}封面`} /><input type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => chooseServiceCover(service.id, event)} /></div></label>
          </div>
          <div className="admin-v2-service-actions">
            <button type="button" onClick={() => saveService(service)}>保存</button>
            <button type="button" onClick={() => moveService(index, -1)} disabled={index === 0}>上移</button>
            <button type="button" onClick={() => moveService(index, 1)} disabled={index === game.services.length - 1}>下移</button>
            <button type="button" onClick={() => toggleService(service)}>{service.is_active ? "隐藏" : "展示"}</button>
          </div>
          <div className="admin-v2-child-services">
            <h3>子服务</h3>
            <div className="admin-v2-child-service-list">
              {service.child_services.map((childService, childIndex) => (
                <section className="admin-v2-child-service-card" key={childService.id}>
                  <label className="admin-v2-field"><span>子服务名称</span><input value={childService.name} onChange={(event) => updateChildService(service.id, childService.id, "name", event.target.value)} /></label>
                  <label className="admin-v2-field"><span>子服务价格</span><input value={childService.price} onChange={(event) => updateChildService(service.id, childService.id, "price", event.target.value)} /></label>
                  <label className="admin-v2-field"><span>子服务说明</span><textarea value={childService.description} onChange={(event) => updateChildService(service.id, childService.id, "description", event.target.value)} /></label>
                  <div className="admin-v2-child-service-actions">
                    <button type="button" onClick={() => saveChildService(childService)}>保存子服务</button>
                    <button type="button" onClick={() => moveChildService(service, childIndex, -1)} disabled={childIndex === 0}>上移</button>
                    <button type="button" onClick={() => moveChildService(service, childIndex, 1)} disabled={childIndex === service.child_services.length - 1}>下移</button>
                    <button type="button" onClick={() => deleteChildService(childService)}>删除</button>
                  </div>
                </section>
              ))}
              {!service.child_services.length && <p className="admin-v2-child-empty">暂无子服务。</p>}
            </div>
            <form className="admin-v2-add-child-service" onSubmit={(event) => addChildService(service, event)}>
              <input required placeholder="子服务名称，例如：11" value={draft.name} onChange={(event) => updateNewChildService(service.id, "name", event.target.value)} />
              <input required placeholder="价格，例如：¥ 30" value={draft.price} onChange={(event) => updateNewChildService(service.id, "price", event.target.value)} />
              <textarea placeholder="子服务简介" value={draft.description} onChange={(event) => updateNewChildService(service.id, "description", event.target.value)} />
              <button className="admin-v2-secondary">添加子服务</button>
            </form>
          </div>
        </article>;
      })}</div>
      <form className="admin-v2-add-service" onSubmit={addService}>
        <h2>新增服务</h2>
        <input required placeholder="服务名称" value={newService.name} onChange={(event) => setNewService({ ...newService, name: event.target.value })} />
        <textarea placeholder="服务说明" value={newService.description} onChange={(event) => setNewService({ ...newService, description: event.target.value })} />
        <div className="admin-v2-save-line"><button className="admin-v2-primary">添加服务</button></div>
      </form>
    </section>
  </AdminLayout>;
}
