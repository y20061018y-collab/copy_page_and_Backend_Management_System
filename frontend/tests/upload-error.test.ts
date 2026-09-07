import { describe, expect, it } from "vitest";
import { uploadErrorMessage } from "../lib/upload-error";

describe("uploadErrorMessage", () => {
  it("explains nginx request-size failures", async () => {
    const response = new Response("Request Entity Too Large", { status: 413 });

    await expect(uploadErrorMessage(response)).resolves.toBe(
      "图片过大，超过服务器上传限制。请压缩图片，或联系管理员调整上传限制。",
    );
  });

  it("uses backend upload messages when available", async () => {
    const response = Response.json({ message: "图片不能超过 5MB" }, { status: 413 });

    await expect(uploadErrorMessage(response)).resolves.toBe(
      "图片过大，超过服务器上传限制。请压缩图片，或联系管理员调整上传限制。",
    );
  });

  it("uses nested FastAPI detail messages", async () => {
    const response = Response.json({ detail: { message: "图片内容无效" } }, { status: 422 });

    await expect(uploadErrorMessage(response)).resolves.toBe("图片内容无效");
  });
});
