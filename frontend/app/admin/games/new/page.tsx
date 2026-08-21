"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function NewGame() {
  const router = useRouter(); const [form, setForm] = useState({ name: "", slug: "", tag: "", description: "", cover_image: "/images/games/原神.jpg", accent_color: "#7c3aed", accent_color_2: "#06b6d4", sort_order: 0, is_active: true }); const [error, setError] = useState("");
  const save = async (event: FormEvent) => { event.preventDefault(); const response = await fetch("/api/admin/games", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) }); if (response.ok) router.push(`/admin/games/${(await response.json()).id}`); else setError("保存失败，请检查 Slug 是否重复"); };
  const update = (key: string, value: string | number) => setForm((current) => ({ ...current, [key]: value }));
  return <main className="admin-shell"><nav className="admin-nav"><strong>11号电竞后台</strong><a href="/admin">概览</a><a href="/admin/games">游戏管理</a><a href="/admin/settings">网站设置</a></nav><section className="dashboard"><p className="eyebrow">NEW GAME</p><h1>新增游戏</h1><form className="settings-form" onSubmit={save}><label>游戏名称<input required value={form.name} onChange={(event) => update("name", event.target.value)} /></label><label>Slug<input required value={form.slug} onChange={(event) => update("slug", event.target.value)} /></label><label>标签<input value={form.tag} onChange={(event) => update("tag", event.target.value)} /></label><label>简介<textarea value={form.description} onChange={(event) => update("description", event.target.value)} /></label><label>排序值<input type="number" value={form.sort_order} onChange={(event) => update("sort_order", Number(event.target.value))} /></label>{error && <p className="form-error">{error}</p>}<button className="admin-action">创建游戏</button></form></section></main>;
}
