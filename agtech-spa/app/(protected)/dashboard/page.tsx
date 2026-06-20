"use client";

import { useAuthContext } from "@/contexts/AuthContext";

export default function DashboardPage() {
  const { user } = useAuthContext();

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Dashboard
      </h1>
      <p style={{ color: "#64748b", margin: "0 0 1.5rem", fontSize: "0.9rem" }}>
        Bienvenido{user?.name ? `, ${user.name}` : ""} — resumen del sistema
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
        }}
      >
        <DashboardCard title="Campos" value="—" />
        <DashboardCard title="Cultivos" value="—" />
        <DashboardCard title="Alertas activas" value="—" />
        <DashboardCard title="Sensores" value="—" />
      </div>
    </div>
  );
}

function DashboardCard({ title, value }: { title: string; value: string }) {
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "8px",
        border: "1px solid #e2e8f0",
        padding: "1.2rem",
      }}
    >
      <p style={{ margin: "0 0 0.5rem", color: "#64748b", fontSize: "0.85rem" }}>
        {title}
      </p>
      <p style={{ margin: 0, fontSize: "1.8rem", fontWeight: 700 }}>{value}</p>
    </div>
  );
}
