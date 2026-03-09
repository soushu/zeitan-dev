"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "計算" },
  { href: "/dashboard", label: "ダッシュボード" },
  { href: "/history", label: "履歴" },
];

export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-6 text-sm font-medium">
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
  );
}
