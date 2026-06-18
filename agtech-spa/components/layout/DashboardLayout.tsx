"use client";

import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";

export function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f1f5f9" }}>
      <Sidebar />
      <main
        style={{
          flex: 1,
          padding: "1.5rem 2rem",
          overflowY: "auto",
          maxWidth: "calc(100vw - 240px)",
        }}
      >
        {children}
      </main>
    </div>
  );
}
