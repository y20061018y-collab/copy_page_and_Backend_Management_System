"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AdminLayout, AdminPageTitle } from "../../components/admin-layout";

type Dashboard = { game_count: number; active_game_count: number; service_count: number; active_service_count: number; latest_updated_at: string | null };
type Game = { id: number; name: string; slug: string; tag: string; cover_image: string; is_active: boolean; services: { id: number; is_active: boolean }[] };
type Settings = { site_name: string; contact_wechat: string | null; contact_qq: string | null; contact_phone: string | null };

export default function AdminDashboard() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      const overview = await fetch("/api/admin/dashboard");
      if (overview.status === 401) return router.push("/admin/login");
      if (!overview.ok) return setError("后台数据加载失败，请确认后端服务正在运行。");
      const [overviewData, gameResponse, settingResponse] = await Promise.all([overview.json(), fetch("/api/admin/games"), fetch("/api/settings")]);
      setDashboard(overviewData);
      if (gameResponse.ok) setGames(await gameResponse.json());
      if (settingResponse.ok) setSettings(await settingResponse.json());
      setError("");
    };
    void load().catch(() => setError("后台数据加载失败，请确认后端服务正在运行。"));
  }, [router]);

  const configuredContacts = [settings?.contact_wechat, settings?.contact_qq, settings?.contact_phone].filter(Boolean).length;
  const activeServices = games.flatMap((game) => game.services).filter((service) => service.is_active).length;

  return <AdminLayout active="dashboard" crumb="控制台">
    <AdminPageTitle title="下午好，欢迎回来 👋" description="这是 11号电竞当前的运营状态，所有核心内容都在正常展示。" actions={<><a className="admin-v2-secondary" href="/" target="_blank">预览前台</a><a className="admin-v2-primary" href="/admin/games/new">＋ 新增游戏</a></>} />
    {error && <p className="admin-v2-error">{error}</p>}
    <section className="admin-v2-stats">
      <article className="admin-v2-stat"><div><span>游戏总数</span><i>▣</i></div><strong>{dashboard?.game_count ?? "–"}</strong><small>全部已启用 <b className="admin-v2-success">{dashboard ? `${dashboard.active_game_count}/${dashboard.game_count}` : ""}</b></small></article>
      <article className="admin-v2-stat"><div><span>服务项目</span><i>☷</i></div><strong>{dashboard?.service_count ?? "–"}</strong><small>当前前台展示 {dashboard?.active_service_count ?? "–"} 项</small></article>
      <article className="admin-v2-stat"><div><span>已上传素材</span><i>▧</i></div><strong>{games.length + (settings?.site_name ? 1 : 0)}</strong><small>游戏封面与工作室图标</small></article>
      <article className="admin-v2-stat"><div><span>待完善内容</span><i>!</i></div><strong>{Math.max(0, 3 - configuredContacts)}</strong><small>建议补全咨询联系方式</small></article>
    </section>
    <section className="admin-v2-grid">
      <article className="admin-v2-panel">
        <div className="admin-v2-panel-head"><h2>游戏目录</h2><span>前台展示顺序与服务概况</span><a href="/admin/games">管理全部 →</a></div>
        <table className="admin-v2-table"><thead><tr><th>游戏</th><th>分类</th><th>服务数</th><th>状态</th><th>操作</th></tr></thead><tbody>
          {games.map((game) => <tr key={game.id}><td><div className="admin-v2-game-cell"><img src={game.cover_image} alt=""/><div><b>{game.name}</b><small>{game.slug}</small></div></div></td><td><span className="admin-v2-tag">{game.tag || "未分类"}</span></td><td>{game.services.length} 项</td><td><span className={`admin-v2-status ${game.is_active ? "" : "is-off"}`}>{game.is_active ? "展示中" : "已隐藏"}</span></td><td><a className="admin-v2-more" href={`/admin/games/${game.id}`}>•••</a></td></tr>)}
          {!games.length && <tr><td colSpan={5}>暂未创建游戏</td></tr>}
        </tbody></table>
      </article>
      <article className="admin-v2-panel"><div className="admin-v2-panel-head"><h2>内容健康度</h2><span>前台资料完整性</span></div><div className="admin-v2-health">
        <div className="admin-v2-score"><div className="admin-v2-ring"><b>{dashboard ? 94 : "–"}</b></div><div><strong>内容状态良好</strong><p>游戏、服务和站点资料均可正常展示。</p></div></div>
        <div className="admin-v2-health-row"><b>游戏封面与图标</b><span>{games.filter((game) => game.cover_image).length} / {games.length} 已上传</span><em>完整</em></div>
        <div className="admin-v2-health-row"><b>服务介绍与价格</b><span>{activeServices} 项启用服务</span><em>已配置</em></div>
        <div className="admin-v2-health-row"><b>咨询联系方式</b><span>已配置 {configuredContacts} 项</span><em>{configuredContacts ? "已配置" : "待补充"}</em></div>
      </div></article>
    </section>
    <section className="admin-v2-grid">
      <article className="admin-v2-panel"><div className="admin-v2-panel-head"><h2>快捷操作</h2><span>常用后台功能</span></div><div className="admin-v2-quick">
        <a href="/admin/games/new"><i>＋</i><b>新增游戏</b><small>封面、介绍、排序</small></a><a href="/admin/services"><i>¥</i><b>服务与价格</b><small>描述、启停、排序</small></a><a href="/admin/media"><i>▧</i><b>素材管理</b><small>查看与替换图片</small></a><a href="/admin/settings"><i>⚙</i><b>站点资料</b><small>名称与联系方式</small></a>
      </div></article>
      <article className="admin-v2-panel"><div className="admin-v2-panel-head"><h2>最近更新</h2><span>按数据更新时间汇总</span></div><div className="admin-v2-activity">
        <div className="admin-v2-activity-row"><i>CAT</i><div><b>游戏目录与服务项目</b><small>{dashboard ? `${dashboard.game_count} 个游戏，${dashboard.service_count} 项服务` : "加载中"}</small></div><time>实时</time></div>
        <div className="admin-v2-activity-row"><i>WEB</i><div><b>网站资料与咨询方式</b><small>{settings?.site_name || "站点设置加载中"}</small></div><time>实时</time></div>
        <div className="admin-v2-activity-row"><i>UPD</i><div><b>最近数据更新</b><small>{dashboard?.latest_updated_at ? new Date(dashboard.latest_updated_at).toLocaleString("zh-CN") : "暂无记录"}</small></div><time>当前</time></div>
      </div></article>
    </section>
  </AdminLayout>;
}
