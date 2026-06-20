"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthContext } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { roleLabel } from "@/lib/auth/roles";

interface NavSubItem {
  label: string;
  href: string;
}

interface NavItem {
  label: string;
  href: string;
  icon: string;
  adminOnly?: boolean;
  agronomoOnly?: boolean;
  sub?: NavSubItem[];
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "📊" },
  { label: "Campos", href: "/campos", icon: "🌾" },
  {
    label: "Catálogos", href: "#", icon: "⚙️", sub: [
      { label: "Cultivos", href: "/cultivos" },
      { label: "Reglas", href: "/reglas" },
    ],
  },
  {
    label: "Analítica", href: "#", icon: "📈", agronomoOnly: true, sub: [
      { label: "Alertas y Recomendaciones", href: "/analytics/recomendaciones" },
      { label: "Predicciones", href: "/analytics/predicciones" },
    ],
  },
  { label: "Datos externos", href: "/external-data", icon: "🛰️", agronomoOnly: true },
  {
    label: "Administración", href: "#", icon: "🔧", adminOnly: true, sub: [
      { label: "Usuarios", href: "/usuarios" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthContext();
  const { theme, toggle } = useTheme();

  function canSee(item: NavItem): boolean {
    if (item.adminOnly && user?.role !== "ADMIN") return false;
    if (item.agronomoOnly && user?.role !== "ADMIN" && user?.role !== "AGRONOMO") return false;
    return true;
  }

  const linkBase: React.CSSProperties = {
    display: "block",
    padding: "0.5rem 0.75rem",
    fontSize: "0.9rem",
    borderRadius: "8px",
    textDecoration: "none",
    transition: "all var(--transition)",
    marginBottom: "2px",
  };

  return (
    <aside
      style={{
        width: "var(--sidebar-width)",
        minWidth: "var(--sidebar-width)",
        background: "var(--bg-glass)",
        backdropFilter: "var(--blur-lg)",
        WebkitBackdropFilter: "var(--blur-lg)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
      }}
    >
      <div style={{ padding: "1.25rem 1.25rem 0.75rem", borderBottom: "1px solid var(--border)" }}>
        <h1 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
          AgTech UNS
        </h1>
      </div>

      <nav style={{ flex: 1, padding: "0.75rem", overflowY: "auto" }}>
        {NAV_ITEMS.filter(canSee).map((item) => {
          const isActive = item.sub
            ? item.sub.some((s) => pathname === s.href)
            : pathname.startsWith(item.href);
          return (
            <div key={item.label} style={{ marginBottom: "0.25rem" }}>
              {item.sub ? (
                <>
                  <div
                    style={{
                      padding: "0.5rem 0.75rem",
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      color: "var(--text-muted)",
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
                          ...linkBase,
                          paddingLeft: "1.75rem",
                          color: subActive ? "var(--accent)" : "var(--text-secondary)",
                          background: subActive
                            ? "var(--accent-bg)"
                            : "transparent",
                        }}
                        onMouseEnter={(e) => {
                          if (!subActive) {
                            e.currentTarget.style.background = "var(--bg-glass-hover)";
                            e.currentTarget.style.color = "var(--text-primary)";
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!subActive) {
                            e.currentTarget.style.background = "transparent";
                            e.currentTarget.style.color = "var(--text-secondary)";
                          }
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
                    ...linkBase,
                    color: isActive ? "var(--accent)" : "var(--text-secondary)",
                    background: isActive ? "var(--accent-bg)" : "transparent",
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "var(--bg-glass-hover)";
                      e.currentTarget.style.color = "var(--text-primary)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "transparent";
                      e.currentTarget.style.color = "var(--text-secondary)";
                    }
                  }}
                >
                  {item.icon} {item.label}
                </Link>
              )}
            </div>
          );
        })}
      </nav>

      <div style={{ padding: "0.75rem", borderTop: "1px solid var(--border)" }}>
        <div style={{ marginBottom: "0.4rem", color: "var(--text-secondary)", wordBreak: "break-all", fontSize: "0.85rem" }}>
          {user?.email}
        </div>
        <div style={{ marginBottom: "0.5rem", color: "var(--text-muted)", fontSize: "0.75rem" }}>
          Rol: {user?.role ? roleLabel(user.role) : "—"}
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={toggle}
            title={`Cambiar a modo ${theme === "dark" ? "claro" : "oscuro"}`}
            style={{
              flex: 1,
              background: "var(--bg-glass)",
              border: "1px solid var(--border)",
              color: "var(--text-secondary)",
              padding: "0.4rem",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "0.85rem",
              transition: "all var(--transition)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-glass-hover)";
              e.currentTarget.style.borderColor = "var(--border-hover)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--bg-glass)";
              e.currentTarget.style.borderColor = "var(--border)";
            }}
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
          <button
            onClick={logout}
            style={{
              flex: 1,
              background: "var(--bg-glass)",
              border: "1px solid var(--border)",
              color: "var(--text-secondary)",
              padding: "0.4rem 0.8rem",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "0.85rem",
              transition: "all var(--transition)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--bg-glass-hover)";
              e.currentTarget.style.borderColor = "var(--border-hover)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--bg-glass)";
              e.currentTarget.style.borderColor = "var(--border)";
            }}
          >
            Salir
          </button>
        </div>
      </div>
    </aside>
  );
}
