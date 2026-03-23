"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { NavLinks } from "@/components/NavLinks";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (!user) return null;

  return (
    <>
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur">
        <div className="relative mx-auto flex h-12 sm:h-14 max-w-5xl items-center justify-between px-4">
          <Link href="/dashboard" className="text-base sm:text-lg font-bold tracking-tight">
            Zeitan
          </Link>
          <NavLinks />
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-3 sm:px-4 py-4 sm:py-8">
        {children}
      </main>
    </>
  );
}
