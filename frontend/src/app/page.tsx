import Link from "next/link";
export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">MediClaim AI</h1>
      <p>AI-powered health insurance claim fraud detection and adjudication.</p>
      <div className="flex gap-3">
        <Link href="/login" className="bg-blue-600 text-white px-4 py-2 rounded">Login</Link>
        <Link href="/dashboard" className="bg-gray-200 px-4 py-2 rounded">Dashboard</Link>
        <Link href="/claims" className="bg-gray-200 px-4 py-2 rounded">Claims</Link>
      </div>
    </div>
  );
}