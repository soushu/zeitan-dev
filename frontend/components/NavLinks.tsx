"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "計算" },
  { href: "/dashboard", label: "ダッシュボード" },
  { href: "/history", label: "履歴" },
];

export function NavLinks() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Desktop nav */}
      <nav className="hidden sm:flex gap-6 text-sm font-medium">
        {links.map(({ href, label }) => {
          const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
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
              const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
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
          </div>
        </nav>
      )}
    </>
  );
}
