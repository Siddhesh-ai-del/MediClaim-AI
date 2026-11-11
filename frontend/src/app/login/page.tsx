"use client";
import { useState } from "react";
import { login } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@demo.med");
  const [password, setPassword] = useState("AdminPass123!");
  const [err, setErr] = useState("");
  const router = useRouter();
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login(email, password);
      router.push("/claims");
    } catch (e: any) {
      setErr(e.message);
    }
  }
  return (
    <form onSubmit={submit} className="max-w-sm space-y-3">
      <h1 className="text-xl font-bold">Login</h1>
      <input className="w-full border p-2 rounded" value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
      <input className="w-full border p-2 rounded" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" />
      {err && <p className="text-red-600 text-sm">{err}</p>}
      <button className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">Sign in</button>
    </form>
  );
}