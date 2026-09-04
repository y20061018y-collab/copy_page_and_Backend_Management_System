import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PublicHome, {
  ServiceModal,
  featuredServices,
  gameDetails,
  modalRows,
  type Game,
  type Settings,
} from "../components/public-home";

describe("public game cards", () => {
  it("has all four local game cover assets", async () => {
    const covers = ["原神.jpg", "崩坏·星穹铁道.jpg", "绝区零.jpg", "鸣潮.jpg"];
    for (const cover of covers) expect(existsSync(resolve(process.cwd(), "public/images/games", cover))).toBe(true);
  });

  it("keeps compact public catalog text at a readable minimum size", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");

    expect(css).toMatch(/\.gameButton small\s*\{[^}]*font-size:\s*(?:1[2-9]|[2-9]\d)px;/);
    expect(css).toMatch(/\.demandCard i\s*\{[^}]*font-size:\s*(?:1[2-9]|[2-9]\d)px;/);
  });

  it("keeps the game and demand panels side by side at every viewport width", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");
    const source = readFileSync(resolve(process.cwd(), "components/public-home.tsx"), "utf8");

    expect(css).toMatch(/@media \(max-width: 800px\)\s*\{[\s\S]*?\.workspace\s*\{\s*grid-template-columns:\s*minmax\(190px,\s*0\.95fr\)\s+minmax\(0,\s*1\.15fr\);/);
    expect(css).not.toMatch(/@media \(max-width: 479px\)/);
    expect(source).not.toMatch(/matchMedia|scrollIntoView|demandsRef|isMobile|id="games"/);
  });

  it("keeps a minimum width on the game panel so game names never collapse", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");

    expect(css).toMatch(/grid-template-columns:\s*minmax\(\d{3}px,\s*0\.95fr\)\s+minmax\(0,\s*1\.15fr\)/);
  });

  it("limits public demand cards to five enabled services", () => {
    const services = Array.from({ length: 6 }, (_, index) => ({
      id: index + 1,
      name: `服务 ${index + 1}`,
      price: `¥ ${index + 1}`,
      description: `服务说明 ${index + 1}`,
    }));
    const result = featuredServices(services);

    expect(result).toEqual(services.slice(0, 5));
    expect(result[0]).toBe(services[0]);
    expect(result[4]).toBe(services[4]);
  });

  it("keeps every available service when there are fewer than five", () => {
    const services = Array.from({ length: 4 }, (_, index) => ({
      id: index + 1,
      name: `服务 ${index + 1}`,
      price: `¥ ${index + 1}`,
      description: `服务说明 ${index + 1}`,
    }));
    const result = featuredServices(services);

    expect(result).toEqual(services);
    expect(result[0]).toBe(services[0]);
    expect(result[3]).toBe(services[3]);
  });

  it("keeps a selected service's child projects in API order", () => {
    const items = [
      { id: 1, name: "日常委托", price: "¥ 30", description: "完成每日委托" },
      { id: 2, name: "深渊满星", price: "¥ 88", description: "挑战深境螺旋" },
      { id: 3, name: "角色培养", price: "¥ 120", description: "规划角色资源" },
    ];
    const result = modalRows(items);

    expect(result).toBe(items);
    expect(result).toEqual(items);
  });

  it("uses game API tag and description without known-slug overrides", () => {
    const game = { tag: "账号代练", description: "按账号进度提供服务" };

    expect(gameDetails(game)).toEqual([game.tag, game.description]);
  });

  it("renders the current game's API cover in the service modal", () => {
    const game: Game = {
      id: 9,
      name: "测试游戏 API 名称",
      slug: "custom-api-game",
      tag: "自定义分类",
      description: "来自接口的游戏说明",
      cover_image: "/api-game-cover.png",
      accent_color: "#123456",
      accent_color_2: "#654321",
      services: [{ id: 41, name: "定制开荒", description: "根据存档制定路线", cover_image: "/custom-service-cover.png", items: [] }],
    };

    const html = renderToStaticMarkup(
      createElement(ServiceModal, {
        game,
        selectedService: game.services[0],
        onClose: () => {},
      }),
    );

    expect(html).toContain('src="/custom-service-cover.png"');
  });

  it("renders only the clicked large project's child projects in the modal", () => {
    const selectedService = {
      id: 41,
      name: "深渊挑战",
      price: "¥ 88",
      description: "外层大项目",
      items: [{ id: 411, name: "12 层满星", price: "¥ 120", description: "完成深渊目标" }],
    };
    const game: Game = {
      id: 9,
      name: "测试游戏",
      slug: "test-game",
      tag: "测试",
      description: "测试说明",
      cover_image: "/test-game.jpg",
      accent_color: "#123456",
      accent_color_2: "#654321",
      services: [selectedService, { id: 42, name: "不应出现的同级大项目", price: "¥ 30", description: "", items: [] }],
    };

    const html = renderToStaticMarkup(createElement(ServiceModal, { game, selectedService, onClose: () => {} }));

    expect(html).toContain("12 层满星");
    expect(html).not.toContain("不应出现的同级大项目");
    expect(html).toContain("测试游戏 · 深渊挑战");
    expect(html).not.toContain("子项目详情");
  });

  it("uses the bundled studio image for all public brand nodes when no image is configured", () => {
    const html = renderToStaticMarkup(
      createElement(PublicHome, {
        games: [
          {
            id: 1,
            name: "测试游戏",
            slug: "test-game",
            tag: "测试",
            description: "测试描述",
            cover_image: "/test-game.jpg",
            accent_color: "#000000",
            accent_color_2: "#ffffff",
            services: [],
          },
        ],
        settings: {
          site_name: "11号电竞工作室",
          site_subtitle: "专业游戏服务",
          studio_image: null,
          contact_wechat: null,
          contact_qq: null,
          contact_phone: null,
          contact_description: null,
        },
      }),
    );

    expect(html.match(/src="\/images\/studio\.jpg"/g)).toHaveLength(3);
  });

  it("uses the configured studio image for the header, hero emblem, and footer", () => {
    const studioImage = "https://cdn.example.com/studio.jpg";
    const html = renderToStaticMarkup(
      createElement(PublicHome, {
        games: [
          {
            id: 1,
            name: "测试游戏",
            slug: "test-game",
            tag: "测试",
            description: "测试描述",
            cover_image: "/test-game.jpg",
            accent_color: "#000000",
            accent_color_2: "#ffffff",
            services: [],
          },
        ],
        settings: {
          site_name: "11号电竞工作室",
          site_subtitle: "专业游戏服务",
          studio_image: studioImage,
          contact_wechat: null,
          contact_qq: null,
          contact_phone: null,
          contact_description: null,
        },
      }),
    );
    const sourcePositions = [...html.matchAll(new RegExp(`src="${studioImage}"`, "g"))].map(
      (match) => match.index,
    );

    expect(sourcePositions).toHaveLength(3);
    expect(sourcePositions[0]).toBeLessThan(html.indexOf("</header>"));
    expect(sourcePositions[1]).toBeGreaterThan(html.indexOf('aria-hidden="true"'));
    expect(sourcePositions[1]).toBeLessThan(html.indexOf("<footer"));
    expect(sourcePositions[2]).toBeGreaterThan(html.indexOf("<footer"));
  });

  it("renders supplied game, settings, and ordered service API values", () => {
    const services = [
      { id: 41, name: "定制开荒", price: "¥ 66", description: "根据存档制定路线", items: [{ id: 411, name: "基础开荒", price: "¥ 30", description: "完成基础任务" }] },
      { id: 12, name: "高难挑战", price: "¥ 99", description: "完成限定挑战目标", items: [] },
      { id: 88, name: "资源规划", price: "¥ 45", description: "优化养成资源分配", items: [] },
    ];
    const games: Game[] = [
      {
        id: 9,
        name: "测试游戏 API 名称",
        slug: "custom-api-game",
        tag: "自定义分类",
        description: "来自接口的游戏说明",
        cover_image: "/custom-cover.png",
        accent_color: "#123456",
        accent_color_2: "#654321",
        services,
      },
    ];
    const settings: Settings = {
      site_name: "接口工作室名称",
      site_subtitle: "接口工作室副标题",
      studio_image: "/custom-studio.png",
      contact_wechat: null,
      contact_qq: null,
      contact_phone: null,
      contact_description: null,
    };

    const html = renderToStaticMarkup(createElement(PublicHome, { games, settings }));

    expect(html).toContain("接口工作室名称");
    expect(html).toContain("接口工作室副标题");
    expect(html).toContain("测试游戏 API 名称");
    expect(html).toContain("自定义分类 · 来自接口的游戏说明");
    expect(html).toContain("/custom-cover.png");
    expect(html).toContain("/custom-studio.png");

    const positions = services.map((service) => {
      expect(html).toContain(service.name);
      expect(html).toContain(service.description);
      return html.indexOf(service.name);
    });
    expect(positions).toEqual([...positions].sort((left, right) => left - right));
  });
});
