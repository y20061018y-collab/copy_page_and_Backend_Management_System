export async function uploadErrorMessage(response: Response, fallback = "图片上传失败"): Promise<string> {
  if (response.status === 413) {
    return "图片过大，超过服务器上传限制。请压缩图片，或联系管理员调整上传限制。";
  }

  const body = await response.json().catch(() => null);
  if (body?.message) return body.message;
  if (body?.detail?.message) return body.detail.message;

  return fallback;
}
