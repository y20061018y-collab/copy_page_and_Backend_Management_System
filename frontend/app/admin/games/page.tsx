"use client";

import { useEffect, useState } from "react";

type Game = { id: number; name: string; slug: string; tag: string; description: string; is_active: boolean; sort_order: number; services: { id: number; name: string; price: string; is_active: boolean }[] };
export default function AdminGames() {
  const [games, setGames] = useState<Game[]>([]); const [filter, setFilter] = useState("all");
  const load = () => fetch("/api/admin/games").then((response) => response.ok ? response.json() : []).then(setGames);
  useEffect(() => { void load(); }, []);
  const toggle = async (game: Game) => { if (!confirm(`${game.is_active ? "禁用" : "启用"} ${game.name}？`)) return; await fetch(`/api/admin/games/${game.id}/state/${game.is_active ? "disable" : "enable"}`, { method: "POST" }); load(); };
  const visible = games.filter((game) => filter === "all" || (filter === "active" ? game.is_active : !game.is_active));
  return <main className="admin-shell"><nav className="admin-nav"><strong>11号电竞后台</strong><a href="/admin">概览</a><a href="/admin/games">游戏管理</a></nav><section className="dashboard"><div className="admin-title"><div><p className="eyebrow">CONTENT</p><h1>游戏管理</h1></div><button className="admin-action">新增游戏</button></div><div className="filters">{[["all", "全部"], ["active", "启用"], ["inactive", "禁用"]].map(([value, label]) => <button className={filter === value ? "selected" : ""} key={value} onClick={() => setFilter(value)}>{label}</button>)}</div><div className="admin-game-list">{visible.map((game) => <article key={game.id}><div><strong>{game.name}</strong><span>{game.slug} · {game.tag}</span></div><div><span>{game.services.length} 个服务</span><button onClick={() => toggle(game)}>{game.is_active ? "禁用" : "恢复"}</button></div></article>)}</div></section></main>;
}
