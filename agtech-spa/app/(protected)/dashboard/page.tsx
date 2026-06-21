"use client";

import { useAuthContext } from "@/contexts/AuthContext";
import { Card } from "@/components/ui";

export default function DashboardPage() {
  const { user } = useAuthContext();

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: "0 0 0.3rem", letterSpacing: "-0.02em" }}>
          Dashboard
        </h1>
        <p style={{ color: "var(--text-muted)", margin: 0, fontSize: "0.9rem" }}>
          Bienvenido{user?.name ? `, ${user.name}` : ""} — resumen del sistema
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
        }}
      >
        <DashboardCard title="Campos" value="—" icon="🌾" />
        <DashboardCard title="Cultivos" value="—" icon="🌱" />
        <DashboardCard title="Alertas activas" value="—" icon="⚠️" />
        <DashboardCard title="Sensores" value="—" icon="📡" />
      </div>
    </div>
  );
}

function DashboardCard({ title, value, icon }: { title: string; value: string; icon: string }) {
  return (
    <Card hover>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <p style={{ margin: "0 0 0.5rem", color: "var(--text-secondary)", fontSize: "0.85rem" }}>
            {title}
          </p>
          <p style={{ margin: 0, fontSize: "1.8rem", fontWeight: 700, lineHeight: 1 }}>{value}</p>
        </div>
        <span style={{ fontSize: "1.5rem", opacity: 0.6 }}>{icon}</span>
      </div>
    </Card>
  );
}
