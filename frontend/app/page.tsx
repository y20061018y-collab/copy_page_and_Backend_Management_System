import PublicHome, { type Game, type Settings } from "../components/public-home";

export default async function Home() {
  const baseUrl = process.env.API_URL ?? "http://localhost:8000";
  try {
    const [gamesResponse, settingsResponse] = await Promise.all([fetch(`${baseUrl}/api/games`, { cache: "no-store" }), fetch(`${baseUrl}/api/settings`, { cache: "no-store" })]);
    if (!gamesResponse.ok || !settingsResponse.ok) throw new Error("API unavailable");
    return <PublicHome games={await gamesResponse.json() as Game[]} settings={await settingsResponse.json() as Settings} />;
  } catch { return <main className="data-error"><h1>服务暂时不可用</h1><p>请稍后刷新页面，或联系工作室管理员。</p></main>; }
}
