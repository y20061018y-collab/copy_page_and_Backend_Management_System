import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("admin game cover editing", () => {
  it("previews selected game covers before the explicit save persists them", () => {
    const source = readFileSync(resolve(process.cwd(), "app/admin/games/[id]/page.tsx"), "utf8");
    const chooseCoverBody = source.match(/const chooseCover = async[\s\S]*?const chooseServiceCover/)?.[0] ?? "";

    expect(source).toContain("pendingCoverFile ? await uploadCover(pendingCoverFile) : game.cover_image");
    expect(source).toContain("setCoverPreview(URL.createObjectURL(file))");
    expect(source).toContain("点击保存游戏资料后生效");
    expect(chooseCoverBody).not.toContain("fetch(");
    expect(chooseCoverBody).not.toContain("uploadCover(file)");
  });
});
