type Service = { id: number; name: string; price: string; description: string };
type Game = {
  id: number; name: string; slug: string; tag: string; description: string;
  cover_image: string; accent_color: string; accent_color_2: string; services: Service[];
};

const fallbackGames: Game[] = [
  { id: 1, name: "原神", slug: "genshin", tag: "开放世界 · 角色养成", description: "探索提瓦特，轻松完成养成目标。", cover_image: "/images/games/原神.jpg", accent_color: "#7c3aed", accent_color_2: "#06b6d4", services: [{ id: 1, name: "日常委托", price: "¥ 30", description: "按需求提供专业服务" }] },
  { id: 2, name: "崩坏·星穹铁道", slug: "star-rail", tag: "回合制 · 银河冒险", description: "专业代打，助你快速完成版本内容。", cover_image: "/images/games/崩坏·星穹铁道.jpg", accent_color: "#2563eb", accent_color_2: "#ec4899", services: [{ id: 2, name: "日常任务", price: "¥ 25", description: "按需求提供专业服务" }] },
  { id: 3, name: "绝区零", slug: "zenless-zone-zero", tag: "动作战斗 · 都市幻想", description: "高效完成零号空洞与角色养成服务。", cover_image: "/images/games/绝区零.jpg", accent_color: "#f97316", accent_color_2: "#ef4444", services: [{ id: 3, name: "每日活跃", price: "¥ 20", description: "按需求提供专业服务" }] },
  { id: 4, name: "鸣潮", slug: "wuthering-waves", tag: "开放世界 · 动作冒险", description: "稳定可靠的鸣潮账号养成服务。", cover_image: "/images/games/鸣潮.jpg", accent_color: "#0891b2", accent_color_2: "#8b5cf6", services: [{ id: 4, name: "每日任务", price: "¥ 25", description: "按需求提供专业服务" }] },
];

async function getGames(): Promise<Game[]> {
  try {
    const response = await fetch(`${process.env.API_URL ?? "http://localhost:8000"}/api/games`, { cache: "no-store" });
    if (response.ok) return response.json();
  } catch { /* local fallback keeps the static front page usable during development */ }
  return fallbackGames;
}

export default async function Home() {
  const games = await getGames();
  return <main>
    <nav className="nav"><div className="brand"><span className="brand-mark">11</span><span>号电竞</span></div><span className="nav-subtitle">专业游戏服务工作室</span><a className="consult" href="#contact">立即咨询</a></nav>
    <section className="hero"><p className="eyebrow">ELEVEN ESPORTS STUDIO</p><h1>把游戏交给<br /><em>专业的人</em></h1><p className="hero-copy">稳定 · 高效 · 值得信赖<br />专注每一次成长体验</p><a className="hero-link" href="#games">探索服务 <span>↓</span></a></section>
    <section className="games" id="games"><div className="section-heading"><p className="eyebrow">OUR SERVICES</p><h2>选择你的游戏</h2><p>每一份服务，都为更好的游戏体验而生</p></div><div className="game-grid">{games.map((game) => <article className="game-card" key={game.slug} style={{ "--accent": game.accent_color, "--accent2": game.accent_color_2 } as React.CSSProperties}><div className="cover" style={{ backgroundImage: `url("${game.cover_image}")` }}><span className="game-number">0{game.id}</span><span className="game-tag">{game.tag}</span></div><div className="card-body"><h3>{game.name}</h3><p>{game.description}</p><div className="services">{game.services.slice(0, 3).map((service) => <span key={service.id}>{service.name}</span>)}</div><div className="card-footer"><strong>起始价 <b>{game.services[0]?.price ?? "面议"}</b></strong><span className="arrow">↗</span></div></div></article>)}</div></section>
    <footer id="contact"><div className="brand"><span className="brand-mark">11</span><span>号电竞</span></div><p>专业游戏服务工作室 · 让每一次游戏体验都更进一步</p><small>© 2026 11号电竞工作室</small></footer>
  </main>;
}
