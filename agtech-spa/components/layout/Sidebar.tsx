"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthContext } from "@/contexts/AuthContext";

interface NavSubItem {
  label: string;
  href: string;
}

interface NavItem {
  label: string;
  href: string;
  icon: string;
  adminOnly?: boolean;
  sub?: NavSubItem[];
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "📊" },
  { label: "Campos", href: "/campos", icon: "🌾" },
  { label: "Catálogos", href: "#", icon: "⚙️", sub: [
    { label: "Cultivos", href: "/cultivos" },
    { label: "Reglas", href: "/reglas" },
    { label: "Sensores", href: "/sensores" },
  ]},
  { label: "Administración", href: "#", icon: "🔧", adminOnly: true, sub: [
    { label: "Agricultores", href: "/agricultores" },
  ]},
  { label: "Analítica", href: "#", icon: "📈", sub: [
    { label: "Alertas", href: "/alertas" },
    { label: "Predicciones", href: "/predicciones" },
  ]},
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthContext();

  return (
    <aside
      style={{
        width: 240,
        minWidth: 240,
        background: "#1e293b",
        color: "#e2e8f0",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
      }}
    >
      <div style={{ padding: "1.2rem", borderBottom: "1px solid #334155" }}>
        <h1 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
          AgTech UNS
        </h1>
      </div>

      <nav style={{ flex: 1, padding: "0.8rem", overflowY: "auto" }}>
        {NAV_ITEMS
          .filter((item) => !item.adminOnly || user?.role === "ADMIN")
          .map((item) => {
          const isActive = (item.sub ? item.sub.some((s) => pathname === s.href) : pathname.startsWith(item.href));
          return (
            <div key={item.label} style={{ marginBottom: "0.3rem" }}>
              {item.sub ? (
                <>
                  <div
                    style={{
                      padding: "0.5rem 0.7rem",
                      fontSize: "0.85rem",
                      fontWeight: 600,
                      color: "#94a3b8",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {item.icon} {item.label}
                  </div>
                  {item.sub.map((sub) => {
                    const subActive = pathname === sub.href;
                    return (
                      <Link
                        key={sub.href}
                        href={sub.href}
                        style={{
                          display: "block",
                          padding: "0.45rem 0.7rem 0.45rem 1.8rem",
                          fontSize: "0.9rem",
                          color: subActive ? "#fff" : "#94a3b8",
                          background: subActive ? "#334155" : "transparent",
                          borderRadius: "6px",
                          textDecoration: "none",
                          transition: "background 0.15s, color 0.15s",
                          marginBottom: "2px",
                        }}
                      >
                        {sub.label}
                      </Link>
                    );
                  })}
                </>
              ) : (
                <Link
                  href={item.href}
                  style={{
                    display: "block",
                    padding: "0.5rem 0.7rem",
                    fontSize: "0.9rem",
                    color: isActive ? "#fff" : "#94a3b8",
                    background: isActive ? "#334155" : "transparent",
                    borderRadius: "6px",
                    textDecoration: "none",
                    transition: "background 0.15s, color 0.15s",
                  }}
                >
                  {item.icon} {item.label}
                </Link>
              )}
            </div>
          );
        })}
      </nav>

      <div
        style={{
          padding: "1rem",
          borderTop: "1px solid #334155",
          fontSize: "0.85rem",
        }}
      >
        <div style={{ marginBottom: "0.4rem", color: "#94a3b8", wordBreak: "break-all" }}>
          {user?.email}
        </div>
        <div style={{ marginBottom: "0.6rem", color: "#64748b", fontSize: "0.8rem" }}>
          Rol: {user?.role ?? "—"}
        </div>
        <button
          onClick={logout}
          style={{
            background: "transparent",
            border: "1px solid #475569",
            color: "#e2e8f0",
            padding: "0.4rem 0.8rem",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "0.85rem",
            width: "100%",
          }}
        >
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
