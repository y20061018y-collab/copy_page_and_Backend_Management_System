import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "11号电竞 | 专业游戏服务工作室",
  description: "专业、可靠、高效的游戏服务工作室",
  icons: {
    icon: [
      { url: "/favicon.ico", type: "image/x-icon" },
      { url: "/favicon.png", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: "/favicon.png",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
