"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function NewClaimPage() {
  const [claimNumber, setClaimNumber] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!files || files.length === 0) { setMsg("select files"); return; }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("claim_number", claimNumber || `CLM-${Date.now()}`);
      for (let i = 0; i < files.length; i++) fd.append("files", files[i]);
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002"}/api/v1/claims`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMsg("Created: " + data.id);
      setTimeout(() => router.push(`/claims/${data.id}`), 1000);
    } catch (e: any) {
      setMsg(e.message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <form onSubmit={submit} className="max-w-lg space-y-3">
      <h1 className="text-xl font-bold">New Claim</h1>
      <input className="w-full border p-2 rounded" value={claimNumber} onChange={e=>setClaimNumber(e.target.value)} placeholder="Claim number (optional)" />
      <input type="file" multiple accept=".pdf,image/*" onChange={e=>setFiles(e.target.files)} className="w-full" />
      {msg && <p className="text-sm">{msg}</p>}
      <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">{loading ? "Uploading..." : "Submit"}</button>
    </form>
  );
}