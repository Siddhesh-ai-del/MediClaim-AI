import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = { title: "MediClaim AI", description: "AI health insurance claim fraud detection" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="border-b bg-white">
          <nav className="mx-auto max-w-6xl flex gap-4 p-4 text-sm">
            <Link href="/" className="font-bold">MediClaim AI</Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/claims">Claims</Link>
            <Link href="/claims/new">New Claim</Link>
            <Link href="/login">Login</Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl p-4">{children}</main>
      </body>
    </html>
  );
}