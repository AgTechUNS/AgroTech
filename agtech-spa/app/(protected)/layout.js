"use client";

import { Sidebar } from "@/components/layout/Sidebar";

export default function ProtectedLayout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: "1.5rem", background: "#f8fafc", overflowX: "auto" }}>
        {children}
      </main>
    </div>
  );
}
