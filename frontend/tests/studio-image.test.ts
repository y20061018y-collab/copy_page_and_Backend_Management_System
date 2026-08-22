import { describe, expect, it } from "vitest";
import { MAX_STUDIO_IMAGE_BYTES, prepareStudioImage } from "../lib/studio-image";

const imageFile = (size: number) => ({ size }) as File;

describe("prepareStudioImage", () => {
  it("keeps an image that is already within the upload limit", async () => {
    const original = imageFile(MAX_STUDIO_IMAGE_BYTES);

    const result = await prepareStudioImage(original, async () => {
      throw new Error("图片不应被压缩");
    });

    expect(result).toBe(original);
  });

  it("retries WebP compression until the image fits the upload limit", async () => {
    const qualities: number[] = [];
    const compressed = imageFile(MAX_STUDIO_IMAGE_BYTES - 1);

    const result = await prepareStudioImage(imageFile(MAX_STUDIO_IMAGE_BYTES + 1), async (_, options) => {
      qualities.push(options.quality);
      return qualities.length === 2 ? compressed : imageFile(MAX_STUDIO_IMAGE_BYTES + 1);
    });

    expect(result).toBe(compressed);
    expect(qualities).toEqual([0.9, 0.75]);
  });

  it("rejects an image that cannot be compressed below the upload limit", async () => {
    await expect(
      prepareStudioImage(imageFile(MAX_STUDIO_IMAGE_BYTES + 1), async () => imageFile(MAX_STUDIO_IMAGE_BYTES + 1)),
    ).rejects.toThrow("图片优化后仍超过 5MB");
  });
});
