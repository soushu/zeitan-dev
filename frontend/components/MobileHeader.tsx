"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/dashboard", label: "ダッシュボード" },
  { href: "/calculate", label: "アップロード / 計算" },
  { href: "/history", label: "計算履歴" },
];

export function MobileHeader() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <header className="lg:hidden sticky top-0 z-50 border-b bg-white/95 backdrop-blur">
      <div className="flex h-12 items-center justify-between px-4">
        <Link href="/dashboard" className="text-base font-bold tracking-tight">
          Zeitan
        </Link>
        <button
          onClick={() => setOpen(!open)}
          className="p-2 text-slate-500 hover:text-slate-700"
          aria-label="メニュー"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
            {open ? (
              <path d="M4 4l12 12M16 4L4 16" />
            ) : (
              <path d="M3 5h14M3 10h14M3 15h14" />
            )}
          </svg>
        </button>
      </div>

      {open && (
        <nav className="border-t bg-white shadow-md">
          <div className="flex flex-col py-2">
            {navItems.map(({ href, label }) => {
              const isActive = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className={`px-4 py-3 text-sm font-medium transition-colors hover:bg-slate-50 ${
                    isActive ? "text-slate-900 font-semibold bg-slate-50" : "text-slate-500"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
            {user && (
              <div className="px-4 py-3 border-t flex items-center justify-between">
                <span className="text-xs text-slate-400 truncate">{user.name || user.email}</span>
                <button
                  onClick={() => { logout(); setOpen(false); }}
                  className="text-xs text-red-500 hover:text-red-700 font-medium"
                >
                  ログアウト
                </button>
              </div>
            )}
          </div>
        </nav>
      )}
    </header>
  );
}
