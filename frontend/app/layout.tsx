import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { AuthProvider } from "@/lib/auth-context";
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
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
