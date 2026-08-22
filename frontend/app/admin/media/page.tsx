"use client";

import { useEffect, useState } from "react";
import { AdminLayout, AdminPageTitle } from "../../../components/admin-layout";
type Game = { id: number; name: string; cover_image: string };
type Settings = { studio_image: string | null };
export default function AdminMedia() {
  const [games, setGames] = useState<Game[]>([]); const [settings, setSettings] = useState<Settings | null>(null);
  useEffect(() => { Promise.all([fetch("/api/admin/games"), fetch("/api/settings")]).then(async ([gameResponse, settingsResponse]) => { if (gameResponse.ok) setGames(await gameResponse.json()); if (settingsResponse.ok) setSettings(await settingsResponse.json()); }); }, []);
  const assets = [{ name: "工作室图标", path: settings?.studio_image || "/images/studio.jpg", type: "站点品牌" }, ...games.map((game) => ({ name: `${game.name} · 游戏封面`, path: game.cover_image, type: "游戏目录" }))];
  return <AdminLayout active="media" crumb="媒体素材"><AdminPageTitle eyebrow="MEDIA LIBRARY" title="媒体素材" description="当前使用中的游戏封面与工作室品牌图片。替换素材后会同步到前台。" actions={<a className="admin-v2-primary" href="/admin/settings">更换工作室图标</a>} />
    <section className="admin-v2-media-grid">{assets.map((asset) => <article className="admin-v2-media-card" key={asset.name}><img src={asset.path} alt={asset.name}/><div><b>{asset.name}</b><small>{asset.type} · {asset.path}</small></div></article>)}</section>
    <div className="admin-v2-toolbar" style={{ marginTop: 16 }}><span>游戏封面在对应的“游戏编辑”页上传；工作室图标在“网站设置”页上传。支持 JPG、PNG、WebP，单张最大 5MB。</span><a className="admin-v2-secondary" href="/admin/games">管理游戏封面</a></div>
  </AdminLayout>;
}
