export function redirectIfUnauthorized(response: Pick<Response, "status">, redirect: (path: string) => void): boolean {
  if (response.status !== 401) return false;

  redirect("/admin/login?expired=1");
  return true;
}
