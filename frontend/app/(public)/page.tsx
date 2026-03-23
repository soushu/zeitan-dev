"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { LandingHero } from "@/components/LandingHero";
import { LandingFeatures } from "@/components/LandingFeatures";
import { LandingFooter } from "@/components/LandingFooter";

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (user) return null;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
          <span className="text-lg font-bold tracking-tight">Zeitan</span>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              ログイン
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 transition-colors"
            >
              無料で始める
            </Link>
          </div>
        </div>
      </header>

      <LandingHero />
      <LandingFeatures />

      {/* CTA */}
      <section className="bg-slate-900 py-16 sm:py-20">
        <div className="mx-auto max-w-3xl text-center px-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            無料で今すぐ始めましょう
          </h2>
          <p className="text-slate-400 mb-8">
            アカウント登録は無料。メールアドレスだけで簡単に始められます。
          </p>
          <Link
            href="/login"
            className="inline-block rounded-lg bg-white px-8 py-3 text-base font-semibold text-slate-900 hover:bg-slate-100 transition-colors"
          >
            無料アカウント作成
          </Link>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
