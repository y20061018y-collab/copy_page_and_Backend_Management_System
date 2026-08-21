"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Dashboard = { game_count: number; active_game_count: number; service_count: number; active_service_count: number; latest_updated_at: string | null };
export default function AdminDashboard() {
  const router = useRouter(); const [data, setData] = useState<Dashboard | null>(null);
  useEffect(() => { fetch("/api/admin/dashboard").then(async (response) => { if (response.status === 401) router.push("/admin/login"); else if (response.ok) setData(await response.json()); }); }, [router]);
  const logout = async () => { await fetch("/api/auth/logout", { method: "POST" }); router.push("/admin/login"); };
  return <main className="admin-shell"><nav className="admin-nav"><strong>11号电竞后台</strong><button onClick={logout}>退出登录</button></nav><section className="dashboard"><p className="eyebrow">OVERVIEW</p><h1>数据概览</h1><div className="stats">{[["游戏总数", data?.game_count], ["启用游戏", data?.active_game_count], ["服务总数", data?.service_count], ["启用服务", data?.active_service_count]].map(([label, value]) => <article key={label as string}><span>{label}</span><strong>{value ?? "-"}</strong></article>)}</div><p className="updated">最近更新时间：{data?.latest_updated_at ?? "加载中"}</p></section></main>;
}
