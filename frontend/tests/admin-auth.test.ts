import { describe, expect, it } from "vitest";
import { redirectIfUnauthorized } from "../lib/admin-auth";

describe("redirectIfUnauthorized", () => {
  it("redirects to login when an admin request returns 401", () => {
    let destination = "";

    const handled = redirectIfUnauthorized(new Response(null, { status: 401 }), (path) => {
      destination = path;
    });

    expect(handled).toBe(true);
    expect(destination).toBe("/admin/login?expired=1");
  });

  it("leaves non-authentication failures for the caller to handle", () => {
    const handled = redirectIfUnauthorized(new Response(null, { status: 500 }), () => {
      throw new Error("不应跳转");
    });

    expect(handled).toBe(false);
  });
});
