import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import { AuthProvider } from "@/lib/auth-context";
import { NavLinks } from "@/components/NavLinks";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Zeitan - 暗号資産税金計算",
  description: "暗号資産の損益計算・確定申告サポートツール",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body className={`${geist.className} min-h-screen bg-background antialiased`}>
        <AuthProvider>
          <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur">
            <div className="relative mx-auto flex h-12 sm:h-14 max-w-5xl items-center justify-between px-4">
              <Link href="/" className="text-base sm:text-lg font-bold tracking-tight">
                Zeitan
              </Link>
              <NavLinks />
            </div>
          </header>
          <main className="mx-auto max-w-5xl px-3 sm:px-4 py-4 sm:py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
