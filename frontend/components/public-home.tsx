"use client";

import { useEffect, useState } from "react";

export type Service = { id: number; name: string; price: string; description: string };
export type Game = { id: number; name: string; slug: string; tag: string; description: string; cover_image: string; accent_color: string; accent_color_2: string; services: Service[] };
export type Settings = { site_name: string; site_subtitle: string; studio_image: string | null; contact_wechat: string | null; contact_qq: string | null; contact_phone: string | null; contact_description: string | null };

export default function PublicHome({ games, settings }: { games: Game[]; settings: Settings }) {
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [showContact, setShowContact] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  useEffect(() => { const close = (event: KeyboardEvent) => { if (event.key === "Escape") { setSelectedGame(null); setShowContact(false); } }; window.addEventListener("keydown", close); return () => window.removeEventListener("keydown", close); }, []);
  const copy = async (kind: string, value: string) => { try { await navigator.clipboard.writeText(value.trim()); setCopied(kind); window.setTimeout(() => setCopied(null), 1600); } catch { setCopied(null); } };
  const wechat = settings.contact_wechat?.trim() || null;
  const qq = settings.contact_qq?.trim() || null;
  const phone = settings.contact_phone?.trim() || null;
  return <main>
    <nav className="nav"><div className="brand">{settings.studio_image ? <img className="brand-image" src={settings.studio_image} alt="工作室" /> : <span className="brand-mark">11</span>}<span>{settings.site_name}</span></div><span className="nav-subtitle">{settings.site_subtitle}</span><button className="consult" onClick={() => setShowContact(true)}>立即咨询</button></nav>
    <section className="hero"><p className="eyebrow">ELEVEN ESPORTS STUDIO</p><h1>把游戏交给<br /><em>专业的人</em></h1><p className="hero-copy">稳定 · 高效 · 值得信赖<br />专注每一次成长体验</p><a className="hero-link" href="#games">探索服务 <span>↓</span></a></section>
    <section className="games" id="games"><div className="section-heading"><p className="eyebrow">OUR SERVICES</p><h2>选择你的游戏</h2><p>每一份服务，都为更好的游戏体验而生</p></div><div className="game-grid">{games.map((game) => <button className="game-card" key={game.slug} onClick={() => setSelectedGame(game)} style={{ "--accent": game.accent_color } as React.CSSProperties}><div className="cover" style={{ backgroundImage: `url("${game.cover_image}")` }}><span className="game-number">0{game.id}</span><span className="game-tag">{game.tag}</span></div><div className="card-body"><h3>{game.name}</h3><p>{game.description}</p><div className="services">{game.services.slice(0, 3).map((service) => <span key={service.id}>{service.name}</span>)}</div><div className="card-footer"><strong>起始价 <b>{game.services[0]?.price ?? "面议"}</b></strong><span className="arrow">↗</span></div></div></button>)}</div></section>
    <footer><div className="brand">{settings.studio_image ? <img className="brand-image" src={settings.studio_image} alt="工作室" /> : <span className="brand-mark">11</span>}<span>{settings.site_name}</span></div><p>{settings.site_subtitle}</p><small>© 2026 11号电竞工作室</small></footer>
    {selectedGame && <div className="modal-backdrop" onClick={() => setSelectedGame(null)}><section className="modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}><button className="modal-close" onClick={() => setSelectedGame(null)}>×</button><p className="eyebrow">SERVICE MENU</p><h2>{selectedGame.name}</h2><p className="modal-description">{selectedGame.description}</p>{selectedGame.services.map((service) => <article className="service-row" key={service.id}><div><h3>{service.name}</h3><p>{service.description}</p></div><strong>{service.price}</strong></article>)}</section></div>}
    {showContact && <div className="modal-backdrop" onClick={() => setShowContact(false)}><section className="modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}><button className="modal-close" onClick={() => setShowContact(false)}>×</button><p className="eyebrow">CONTACT US</p><h2>立即咨询</h2><p className="modal-description">{settings.contact_description ?? "欢迎联系我们咨询服务详情"}</p>{wechat && <button className="contact-row" onClick={() => copy("wechat", wechat)}><span>微信</span><strong>{wechat}</strong><small>{copied === "wechat" ? "已复制" : "复制"}</small></button>}{qq && <button className="contact-row" onClick={() => copy("qq", qq)}><span>QQ</span><strong>{qq}</strong><small>{copied === "qq" ? "已复制" : "复制"}</small></button>}{phone && <div className="contact-row"><span>电话</span><strong>{phone}</strong><button onClick={() => copy("phone", phone)}>{copied === "phone" ? "已复制" : "复制"}</button><a href={`tel:${phone}`}>拨打</a></div>}{!wechat && !qq && !phone && <p>联系方式尚未配置，请联系管理员。</p>}</section></div>}
  </main>;
}
