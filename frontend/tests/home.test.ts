import { describe, expect, it } from "vitest";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

describe("public game cards", () => {
  it("has all four local game cover assets", async () => {
    const covers = ["原神.jpg", "崩坏·星穹铁道.jpg", "绝区零.jpg", "鸣潮.jpg"];
    for (const cover of covers) expect(existsSync(resolve(process.cwd(), "public/images/games", cover))).toBe(true);
  });
});
