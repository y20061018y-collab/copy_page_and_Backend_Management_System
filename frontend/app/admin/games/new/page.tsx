"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminLayout, AdminPageTitle } from "../../../../components/admin-layout";
type GameForm = { name: string; slug: string; tag: string; description: string; cover_image: string; accent_color: string; accent_color_2: string; sort_order: number; is_active: boolean };
const initial: GameForm = { name: "", slug: "", tag: "", description: "", cover_image: "/images/games/原神.jpg", accent_color: "#7c3aed", accent_color_2: "#06b6d4", sort_order: 0, is_active: true };
export default function NewGame() {
  const router = useRouter(); const [form, setForm] = useState(initial); const [preview, setPreview] = useState(initial.cover_image); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  const update = <K extends keyof GameForm>(key: K, value: GameForm[K]) => setForm((current) => ({ ...current, [key]: value }));
  const chooseCover = async (event: ChangeEvent<HTMLInputElement>) => { const file = event.target.files?.[0]; if (!file) return; setPreview(URL.createObjectURL(file)); setMessage("图片上传中..."); const body = new FormData(); body.append("file", file); const response = await fetch("/api/admin/uploads/game-cover", { method: "POST", body }); if (!response.ok) return setMessage("图片上传失败"); update("cover_image", (await response.json()).path); setMessage("图片已上传"); };
  const save = async (event: FormEvent) => { event.preventDefault(); setMessage("创建中..."); setError(""); const response = await fetch("/api/admin/games", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) }); if (response.ok) router.push(`/admin/games/${(await response.json()).id}`); else { setMessage(""); setError("保存失败，请检查 Slug 是否重复。"); } };
  return <AdminLayout active="games" crumb="新增游戏"><AdminPageTitle eyebrow="NEW GAME" title="新增游戏" description="创建后可继续在编辑页管理服务项目和前台展示顺序。" actions={<a className="admin-v2-secondary" href="/admin/games">返回目录</a>} />
    <form className="admin-v2-panel admin-v2-form-panel" onSubmit={save}><div className="admin-v2-form-grid">
      <label className="admin-v2-field"><span>游戏名称</span><input required value={form.name} onChange={(event) => update("name", event.target.value)} /></label><label className="admin-v2-field"><span>Slug（唯一英文标识）</span><input required value={form.slug} onChange={(event) => update("slug", event.target.value)} /></label>
      <label className="admin-v2-field"><span>游戏分类</span><input value={form.tag} onChange={(event) => update("tag", event.target.value)} /></label><label className="admin-v2-field"><span>排序值</span><input type="number" value={form.sort_order} onChange={(event) => update("sort_order", Number(event.target.value))} /></label>
      <label className="admin-v2-field is-wide"><span>前台简介</span><textarea value={form.description} onChange={(event) => update("description", event.target.value)} /></label>
      <label className="admin-v2-field"><span>展示状态</span><select value={form.is_active ? "active" : "inactive"} onChange={(event) => update("is_active", event.target.value === "active")}><option value="active">前台展示</option><option value="inactive">暂不展示</option></select></label><label className="admin-v2-field"><span>主色</span><input type="color" value={form.accent_color} onChange={(event) => update("accent_color", event.target.value)} /></label>
      <label className="admin-v2-field"><span>辅助色</span><input type="color" value={form.accent_color_2} onChange={(event) => update("accent_color_2", event.target.value)} /></label><label className="admin-v2-field"><span>游戏封面</span><div className="admin-v2-cover"><img src={preview} alt="游戏预览"/><input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseCover} /></div></label>
    </div>{error && <p className="admin-v2-error">{error}</p>}<div className="admin-v2-save-line"><button className="admin-v2-primary" type="submit">创建游戏</button><span className="admin-v2-message">{message}</span></div></form>
  </AdminLayout>;
}
