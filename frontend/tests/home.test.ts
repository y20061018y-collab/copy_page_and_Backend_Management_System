import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import PublicHome, {
  ServiceModal,
  childServiceRows,
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

  it("uses the approved public catalog mobile breakpoint contract", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");
    const source = readFileSync(resolve(process.cwd(), "components/public-home.tsx"), "utf8");

    expect(css).toMatch(/@media \(max-width: 600px\)\s*\{[\s\S]*?\.workspace\s*\{\s*grid-template-columns:\s*minmax\(150px,\s*0\.76fr\)\s+minmax\(0,\s*1\.24fr\);/);
    expect(css).toMatch(/@media \(max-width: 374px\)\s*\{[\s\S]*?\.workspace\s*\{\s*grid-template-columns:\s*1fr;/);
    expect(source).not.toMatch(/matchMedia|scrollIntoView|demandsRef|isMobile|id="games"/);
  });

  it("keeps a minimum width on the mobile game panel so game names never collapse", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");

    expect(css).toMatch(/@media \(max-width: 600px\)\s*\{[\s\S]*?grid-template-columns:\s*minmax\(150px,\s*0\.76fr\)\s+minmax\(0,\s*1\.24fr\)/);
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

  it("keeps modal service rows in API order", () => {
    const services = [
      { id: 1, name: "日常委托", price: "¥ 30", description: "完成每日委托" },
      { id: 2, name: "深渊满星", price: "¥ 88", description: "挑战深境螺旋" },
      { id: 3, name: "角色培养", price: "¥ 120", description: "规划角色资源" },
    ];
    const result = modalRows(services);

    expect(result).toBe(services);
    expect(result).toEqual(services);
  });

  it("keeps child service rows in API order", () => {
    const childServices = [
      { id: 11, name: "11", price: "¥ 30", description: "完成基础目标与前置内容。", image_path: "/uploads/games/sample.png" },
      { id: 12, name: "12", price: "¥ 88", description: "完成进阶目标。", image_path: null },
    ];

    expect(childServiceRows(childServices)).toBe(childServices);
    expect(childServiceRows(undefined)).toEqual([]);
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
      services: [{ id: 41, name: "定制开荒", price: "¥ 66", description: "根据存档制定路线", cover_image: "/custom-service-cover.png" }],
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

  it("renders the clicked service's direct price in the modal", () => {
    const selectedService = {
      id: 41,
      name: "深渊挑战",
      price: "¥ 88",
      description: "完成深渊挑战",
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
      services: [selectedService, { id: 42, name: "同级服务", price: "¥ 30", description: "" }],
    };

    const html = renderToStaticMarkup(createElement(ServiceModal, { game, selectedService, onClose: () => {} }));

    expect(html).toContain("完成深渊挑战");
    expect(html).toContain("¥ 88");
    expect(html).not.toContain("同级服务");
    expect(html).toContain("测试游戏 · 深渊挑战");
    expect(html).not.toContain(["子", "项目"].join(""));
  });

  it("renders child services with optional images in the service modal", () => {
    const selectedService = {
      id: 41,
      name: "日常委托",
      price: "¥ 30",
      description: "完成每日委托",
      child_services: [
        { id: 11, name: "11", price: "¥ 30", description: "完成基础目标与前置内容。", image_path: "/uploads/games/child.png" },
        { id: 12, name: "12", price: "¥ 88", description: "完成进阶目标。", image_path: null },
      ],
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
      services: [selectedService],
    };

    const html = renderToStaticMarkup(createElement(ServiceModal, { game, selectedService, onClose: () => {} }));

    expect(html).toContain("日常委托");
    expect(html).toContain("完成每日委托");
    expect(html).toContain("完成基础目标与前置内容。");
    expect(html).toContain('src="/uploads/games/child.png"');
    expect(html).toContain("完成进阶目标。");
    expect(html).not.toContain("null");
  });

  it("keeps child service cards responsive at the approved mobile breakpoints", () => {
    const css = readFileSync(resolve(process.cwd(), "components/public-home.module.css"), "utf8");

    expect(css).toMatch(/@media \(max-width: 600px\)\s*\{[\s\S]*?\.childServiceList\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\);/);
    expect(css).toMatch(/@media \(max-width: 374px\)\s*\{[\s\S]*?\.childServiceList\s*\{[\s\S]*?grid-template-columns:\s*1fr;/);
    expect(css).toMatch(/\.childServiceBody strong\s*\{[\s\S]*?white-space:\s*nowrap;/);
    expect(css).toMatch(/\.childServiceBody > div\s*\{[\s\S]*?grid-template-columns:\s*minmax\(0,\s*1fr\)\s+max-content;/);
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
      { id: 41, name: "定制开荒", price: "¥ 66", description: "根据存档制定路线" },
      { id: 12, name: "高难挑战", price: "¥ 99", description: "完成限定挑战目标" },
      { id: 88, name: "资源规划", price: "¥ 45", description: "优化养成资源分配" },
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
