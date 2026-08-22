"use client";

import { ReactNode } from "react";
import { useRouter } from "next/navigation";

export type AdminSection = "dashboard" | "games" | "services" | "media" | "settings" | "account";

type Props = {
  active: AdminSection;
  crumb: string;
  children: ReactNode;
};

const navigation: Array<{ key: AdminSection; href: string; icon: string; label: string }> = [
  { key: "dashboard", href: "/admin", icon: "⌂", label: "控制台" },
  { key: "games", href: "/admin/games", icon: "▣", label: "游戏目录" },
  { key: "services", href: "/admin/services", icon: "☷", label: "服务项目" },
  { key: "media", href: "/admin/media", icon: "▧", label: "媒体素材" },
  { key: "settings", href: "/admin/settings", icon: "⚙", label: "网站设置" },
  { key: "account", href: "/admin/account", icon: "♙", label: "管理员账号" },
];

export function AdminLayout({ active, crumb, children }: Props) {
  const router = useRouter();

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/admin/login");
  };

  return (
    <div className="admin-v2">
      <aside className="admin-v2-sidebar">
        <a className="admin-v2-brand" href="/admin">
          <img src="/images/studio.jpg" alt="11号电竞" />
          <span><b>11号电竞</b><small>运营管理中心</small></span>
        </a>
        <p className="admin-v2-nav-label">WORKSPACE</p>
        <nav className="admin-v2-nav">
          {navigation.slice(0, 4).map((item) => <a key={item.key} className={active === item.key ? "is-active" : ""} href={item.href}><i>{item.icon}</i>{item.label}</a>)}
        </nav>
        <p className="admin-v2-nav-label">SYSTEM</p>
        <nav className="admin-v2-nav">
          {navigation.slice(4).map((item) => <a key={item.key} className={active === item.key ? "is-active" : ""} href={item.href}><i>{item.icon}</i>{item.label}</a>)}
          <a href="/" target="_blank" rel="noreferrer"><i>◎</i>查看前台</a>
        </nav>
        <div className="admin-v2-storage"><b>素材空间</b><span>图片与工作室标识</span><div><i /></div><small>JPG / PNG / WebP，单张最大 5MB</small></div>
      </aside>
      <div className="admin-v2-main">
        <header className="admin-v2-topbar">
          <span className="admin-v2-crumb">工作台 <b>/</b> <strong>{crumb}</strong></span>
          <div className="admin-v2-top-actions">
            <label className="admin-v2-search"><span>⌕</span><input placeholder="搜索游戏、服务或设置" /></label>
            <button type="button" title="通知">◌</button>
            <a href="/" target="_blank" rel="noreferrer" title="打开前台">↗</a>
            <div className="admin-v2-user"><b>11</b><span><strong>超级管理员</strong><small>admin</small></span><button type="button" onClick={logout}>退出</button></div>
          </div>
        </header>
        <main className="admin-v2-content">{children}</main>
      </div>
    </div>
  );
}

export function AdminPageTitle({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) {
  return <section className="admin-v2-page-title"><div>{eyebrow && <p>{eyebrow}</p>}<h1>{title}</h1>{description && <span>{description}</span>}</div>{actions && <div className="admin-v2-page-actions">{actions}</div>}</section>;
}
