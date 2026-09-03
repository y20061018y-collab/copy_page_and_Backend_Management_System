"use client";

import { useEffect, useState } from "react";
import { AdminLayout, AdminPageTitle } from "../../../components/admin-layout";

type Service = { id: number; name: string; description: string; sort_order: number; is_active: boolean };
type Game = { id: number; name: string; cover_image: string; services: Service[] };

export default function AdminServices() {
  const [games, setGames] = useState<Game[]>([]);
  useEffect(() => { fetch("/api/admin/games").then((response) => response.ok ? response.json() : []).then(setGames); }, []);
  const services = games.flatMap((game) => game.services.map((service) => ({ ...service, game })));
  return <AdminLayout active="services" crumb="服务项目"><AdminPageTitle eyebrow="SERVICE CATALOG" title="服务项目" description="按游戏维护服务说明、启停状态与前台展示顺序；价格在子项目中维护。" />
    <div className="admin-v2-toolbar"><span>共 {services.length} 项服务。服务的编辑、排序和启停都在对应游戏的编辑页完成。</span><a className="admin-v2-primary" href="/admin/games">前往游戏目录</a></div>
    <section className="admin-v2-panel"><table className="admin-v2-table"><thead><tr><th>服务项目</th><th>所属游戏</th><th>服务说明</th><th>状态</th><th>编辑</th></tr></thead><tbody>{services.map((service) => <tr key={service.id}><td><b>{service.name}</b></td><td><div className="admin-v2-game-cell"><img src={service.game.cover_image} alt=""/><b>{service.game.name}</b></div></td><td>{service.description || "暂未填写服务说明"}</td><td><span className={`admin-v2-status ${service.is_active ? "" : "is-off"}`}>{service.is_active ? "展示中" : "已隐藏"}</span></td><td><a className="admin-v2-secondary" href={`/admin/games/${service.game.id}`}>编辑</a></td></tr>)}{!services.length && <tr><td colSpan={5}>暂未添加服务项目</td></tr>}</tbody></table></section>
  </AdminLayout>;
}
