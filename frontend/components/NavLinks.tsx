"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const links = [
  { href: "/dashboard", label: "ダッシュボード" },
  { href: "/calculate", label: "計算" },
  { href: "/history", label: "履歴" },
];

export function NavLinks() {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Desktop nav */}
      <div className="hidden sm:flex items-center gap-6">
        <nav className="flex gap-6 text-sm font-medium">
          {links.map(({ href, label }) => {
            const isActive = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={`transition-colors hover:text-foreground ${
                  isActive ? "text-foreground font-semibold" : "text-muted-foreground"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
        {!loading && (
          user ? (
            <div className="flex items-center gap-3 ml-2 border-l pl-4">
              <span className="text-xs text-muted-foreground">{user.name || user.email}</span>
              <button
                onClick={logout}
                className="text-xs text-red-500 hover:text-red-700 font-medium"
              >
                ログアウト
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="ml-2 border-l pl-4 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              ログイン
            </Link>
          )
        )}
      </div>

      {/* Mobile hamburger */}
      <button
        className="sm:hidden p-2 text-muted-foreground hover:text-foreground"
        onClick={() => setOpen(!open)}
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

      {/* Mobile menu overlay */}
      {open && (
        <nav className="sm:hidden absolute top-full left-0 right-0 bg-background border-b shadow-md z-50">
          <div className="flex flex-col py-2">
            {links.map(({ href, label }) => {
              const isActive = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className={`px-4 py-3 text-sm font-medium transition-colors hover:bg-muted ${
                    isActive ? "text-foreground font-semibold bg-muted/50" : "text-muted-foreground"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
            {!loading && (
              user ? (
                <div className="px-4 py-3 border-t flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{user.name || user.email}</span>
                  <button
                    onClick={() => { logout(); setOpen(false); }}
                    className="text-xs text-red-500 hover:text-red-700 font-medium"
                  >
                    ログアウト
                  </button>
                </div>
              ) : (
                <Link
                  href="/login"
                  onClick={() => setOpen(false)}
                  className="px-4 py-3 text-sm font-medium text-blue-600 hover:bg-muted border-t"
                >
                  ログイン
                </Link>
              )
            )}
          </div>
        </nav>
      )}
    </>
  );
}
