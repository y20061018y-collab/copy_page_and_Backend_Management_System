"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function AdminLogin() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const submit = async (event: FormEvent) => { event.preventDefault(); setError(""); const response = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) }); if (response.ok) router.push("/admin"); else setError("账号或密码错误"); };
  return <main className="admin-shell"><form className="admin-form" onSubmit={submit}><p className="eyebrow">11号电竞 ADMIN</p><h1>管理员登录</h1><label>账号<input value={username} onChange={(event) => setUsername(event.target.value)} required /></label><label>密码<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error && <p className="form-error">{error}</p>}<button type="submit">登录后台</button></form></main>;
}
