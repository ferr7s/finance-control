import type { Metadata } from "next";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

import "./globals.css";

export const metadata: Metadata = {
  title: "Finance Control",
  description: "Local-first personal finance dashboard and read-only agent gateway."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body>
        <Sidebar />
        <div className="min-h-screen lg:pl-64">
          <Topbar />
          <main className="mx-auto w-full max-w-7xl px-4 py-6 lg:px-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
