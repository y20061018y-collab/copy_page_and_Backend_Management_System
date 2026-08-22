export const MAX_STUDIO_IMAGE_BYTES = 5 * 1024 * 1024;

type CompressionOptions = {
  maxDimension: number;
  quality: number;
};

export type StudioImageCompressor = (file: File, options: CompressionOptions) => Promise<File>;

const compressionAttempts: CompressionOptions[] = [
  { maxDimension: 1600, quality: 0.9 },
  { maxDimension: 1600, quality: 0.75 },
  { maxDimension: 1280, quality: 0.6 },
  { maxDimension: 1024, quality: 0.45 },
];

export async function prepareStudioImage(file: File, compress: StudioImageCompressor): Promise<File> {
  if (file.size <= MAX_STUDIO_IMAGE_BYTES) return file;

  for (const options of compressionAttempts) {
    const compressed = await compress(file, options);
    if (compressed.size <= MAX_STUDIO_IMAGE_BYTES) return compressed;
  }

  throw new Error("图片优化后仍超过 5MB，请选择尺寸更小的图片");
}

export async function compressStudioImage(file: File, options: CompressionOptions): Promise<File> {
  const image = await loadImage(file);
  const scale = Math.min(1, options.maxDimension / Math.max(image.width, image.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(image.width * scale));
  canvas.height = Math.max(1, Math.round(image.height * scale));

  const context = canvas.getContext("2d");
  if (!context) throw new Error("浏览器不支持图片优化");
  context.drawImage(image, 0, 0, canvas.width, canvas.height);

  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/webp", options.quality));
  if (!blob) throw new Error("图片优化失败");
  return new File([blob], `${file.name.replace(/\.[^.]+$/, "") || "studio"}.webp`, { type: "image/webp" });
}

function loadImage(file: File): Promise<HTMLImageElement> {
  const url = URL.createObjectURL(file);
  const image = new Image();

  return new Promise((resolve, reject) => {
    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("图片无法读取"));
    };
    image.src = url;
  });
}
