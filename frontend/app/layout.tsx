import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "11号电竞 | 专业游戏服务工作室",
  description: "专业、可靠、高效的游戏服务工作室",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
