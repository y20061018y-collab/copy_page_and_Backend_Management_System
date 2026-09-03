"use client";

import { useEffect, useState } from "react";
import { AdminLayout, AdminPageTitle } from "../../../components/admin-layout";

type Game = { id: number; name: string; slug: string; tag: string; description: string; cover_image: string; is_active: boolean; sort_order: number; services: { id: number; name: string; is_active: boolean }[] };

export default function AdminGames() {
  const [games, setGames] = useState<Game[]>([]);
  const [filter, setFilter] = useState("all");
  const load = () => fetch("/api/admin/games").then((response) => response.ok ? response.json() : []).then(setGames);
  useEffect(() => { void load(); }, []);
  const toggle = async (game: Game) => { if (!confirm(`${game.is_active ? "隐藏" : "展示"} ${game.name}？`)) return; await fetch(`/api/admin/games/${game.id}/state/${game.is_active ? "disable" : "enable"}`, { method: "POST" }); void load(); };
  const move = async (index: number, direction: -1 | 1) => { const nextIndex = index + direction; if (nextIndex < 0 || nextIndex >= games.length) return; const reordered = [...games]; [reordered[index], reordered[nextIndex]] = [reordered[nextIndex], reordered[index]]; await fetch("/api/admin/games/reorder", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(reordered.map((game, position) => ({ id: game.id, sort_order: position }))) }); void load(); };
  const visible = games.filter((game) => filter === "all" || (filter === "active" ? game.is_active : !game.is_active));

  return <AdminLayout active="games" crumb="游戏目录">
    <AdminPageTitle eyebrow="CONTENT CATALOG" title="游戏目录" description="维护前台展示的游戏、封面、简介、服务内容和排序。" actions={<a className="admin-v2-primary" href="/admin/games/new"><span aria-hidden="true">＋</span><span>新增游戏</span></a>} />
    <div className="admin-v2-toolbar"><div className="admin-v2-filters">{[["all", "全部游戏"], ["active", "展示中"], ["inactive", "已隐藏"]].map(([value, label]) => <button key={value} className={filter === value ? "is-selected" : ""} onClick={() => setFilter(value)}>{label}</button>)}</div><span>共 {visible.length} 个游戏，排序会同步到前台。</span></div>
    <section className="admin-v2-panel"><table className="admin-v2-table"><thead><tr><th>游戏</th><th>Slug / 分类</th><th>服务项目</th><th>前台状态</th><th>排序</th><th>操作</th></tr></thead><tbody>
      {visible.map((game) => { const sourceIndex = games.findIndex((item) => item.id === game.id); return <tr key={game.id}><td><div className="admin-v2-game-cell"><img src={game.cover_image} alt=""/><div><b>{game.name}</b><small>{game.description || "未填写前台简介"}</small></div></div></td><td><b>{game.slug}</b><br/><span className="admin-v2-tag">{game.tag || "未分类"}</span></td><td>{game.services.length} 项<br/><small>{game.services.filter((service) => service.is_active).length} 项展示中</small></td><td><span className={`admin-v2-status ${game.is_active ? "" : "is-off"}`}>{game.is_active ? "展示中" : "已隐藏"}</span></td><td>{game.sort_order}</td><td><div className="admin-v2-list-actions"><a className="admin-v2-secondary" href={`/admin/games/${game.id}`}>编辑</a><button onClick={() => move(sourceIndex, -1)} disabled={sourceIndex === 0}>上移</button><button onClick={() => move(sourceIndex, 1)} disabled={sourceIndex === games.length - 1}>下移</button><button onClick={() => toggle(game)}>{game.is_active ? "隐藏" : "展示"}</button></div></td></tr>; })}
      {!visible.length && <tr><td colSpan={6}>暂无符合条件的游戏</td></tr>}
    </tbody></table></section>
  </AdminLayout>;
}
