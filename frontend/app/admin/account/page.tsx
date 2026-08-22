"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminLayout, AdminPageTitle } from "../../../components/admin-layout";
type Admin = { id: number; username: string };
export default function AdminAccount() {
  const router = useRouter(); const [admin, setAdmin] = useState<Admin | null>(null);
  useEffect(() => { fetch("/api/auth/me").then((response) => { if (response.status === 401) return router.push("/admin/login"); return response.ok ? response.json() : null; }).then(setAdmin); }, [router]);
  return <AdminLayout active="account" crumb="管理员账号"><AdminPageTitle eyebrow="ACCOUNT & SECURITY" title="管理员账号" description="当前登录身份与后台访问状态。" />
    <section className="admin-v2-panel admin-v2-account"><div className="admin-v2-account-avatar">11</div><div><h2>{admin?.username || "加载中"}</h2><p>拥有游戏目录、服务项目、媒体素材和网站设置的完整管理权限。</p><dl><dt>管理员 ID</dt><dd>{admin?.id ?? "–"}</dd><dt>账号状态</dt><dd><span className="admin-v2-status">正常启用</span></dd><dt>认证方式</dt><dd>账号密码登录 · 安全 Cookie 会话</dd><dt>退出登录</dt><dd>可通过右上角“退出”立即结束当前后台会话。</dd></dl></div></section>
  </AdminLayout>;
}
