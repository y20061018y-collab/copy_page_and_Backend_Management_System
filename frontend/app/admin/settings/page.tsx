"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminLayout, AdminPageTitle } from "../../../components/admin-layout";
import { redirectIfUnauthorized } from "../../../lib/admin-auth";
import { compressStudioImage, prepareStudioImage } from "../../../lib/studio-image";

type Settings = { site_name: string; site_subtitle: string; studio_image: string | null; contact_wechat: string | null; contact_qq: string | null; contact_phone: string | null; contact_description: string | null };
const empty: Settings = { site_name: "", site_subtitle: "", studio_image: null, contact_wechat: "", contact_qq: "", contact_phone: "", contact_description: "" };

export default function AdminSettings() {
  const [settings, setSettings] = useState(empty); const [preview, setPreview] = useState<string | null>(null); const [image, setImage] = useState<File | null>(null); const [message, setMessage] = useState("");
  const router = useRouter();
  useEffect(() => { let cancelled = false; const load = async () => { const auth = await fetch("/api/auth/me"); if (redirectIfUnauthorized(auth, (path) => router.replace(path))) return; const response = await fetch("/api/settings"); if (!cancelled) setSettings(response.ok ? await response.json() : empty); }; void load(); return () => { cancelled = true; }; }, [router]);
  const update = (key: keyof Settings, value: string | null) => setSettings((current) => ({ ...current, [key]: value }));
  const chooseImage = (event: ChangeEvent<HTMLInputElement>) => { const file = event.target.files?.[0]; if (file) { setImage(file); setPreview(URL.createObjectURL(file)); } };
  const save = async (event: FormEvent) => { event.preventDefault(); setMessage("保存中..."); let next = settings; if (image) { try { setMessage(image.size > 5 * 1024 * 1024 ? "正在优化图片..." : "正在上传图片..."); const uploadImage = await prepareStudioImage(image, compressStudioImage); const body = new FormData(); body.append("file", uploadImage); const upload = await fetch("/api/admin/uploads/studio-image", { method: "POST", body }); if (!upload.ok) { if (redirectIfUnauthorized(upload, (path) => router.replace(path))) return setMessage("登录已失效，请重新登录"); return setMessage((await upload.json().catch(() => null))?.message ?? "图片上传失败"); } next = { ...settings, studio_image: (await upload.json()).path }; } catch (error) { return setMessage(error instanceof Error ? error.message : "图片优化失败"); } } const response = await fetch("/api/admin/settings", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(next) }); if (response.ok) { setSettings(await response.json()); setImage(null); setMessage("已保存，前台会立即使用新资料"); } else if (redirectIfUnauthorized(response, (path) => router.replace(path))) setMessage("登录已失效，请重新登录"); else setMessage("保存失败"); };
  return <AdminLayout active="settings" crumb="网站设置"><AdminPageTitle eyebrow="SITE SETTINGS" title="网站设置" description="管理工作室名称、品牌图片和用户咨询方式。" />
    <form className="admin-v2-panel admin-v2-form-panel" onSubmit={save}><div className="admin-v2-form-grid">
      <label className="admin-v2-field"><span>网站名称</span><input value={settings.site_name} onChange={(event) => update("site_name", event.target.value)} required /></label>
      <label className="admin-v2-field"><span>副标题</span><input value={settings.site_subtitle} onChange={(event) => update("site_subtitle", event.target.value)} required /></label>
      <label className="admin-v2-field"><span>微信号</span><input value={settings.contact_wechat ?? ""} onChange={(event) => update("contact_wechat", event.target.value)} /></label>
      <label className="admin-v2-field"><span>QQ 号</span><input value={settings.contact_qq ?? ""} onChange={(event) => update("contact_qq", event.target.value)} /></label>
      <label className="admin-v2-field"><span>联系电话</span><input value={settings.contact_phone ?? ""} onChange={(event) => update("contact_phone", event.target.value)} /></label>
      <label className="admin-v2-field is-wide"><span>咨询提示</span><textarea value={settings.contact_description ?? ""} onChange={(event) => update("contact_description", event.target.value)} /></label>
      <label className="admin-v2-field is-wide"><span>工作室图标</span><div className="admin-v2-cover"><img src={preview || settings.studio_image || "/images/studio.jpg"} alt="工作室图标预览"/><input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseImage} /></div></label>
    </div><div className="admin-v2-save-line"><button className="admin-v2-primary" type="submit">保存网站设置</button><span className="admin-v2-message">{message}</span></div></form>
  </AdminLayout>;
}
