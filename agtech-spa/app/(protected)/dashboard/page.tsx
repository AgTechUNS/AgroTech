"use client";

import { useEffect, useState } from "react";
import { useAuthContext } from "@/contexts/AuthContext";
import { Card } from "@/components/ui";
import { listarCampos } from "@/lib/services/campos";
import { listarCultivos } from "@/lib/services/cultivos";
import { listarSensores } from "@/lib/services/sensores";

export default function DashboardPage() {
  const { user } = useAuthContext();
  const [campos, setCampos] = useState<number | null>(null);
  const [cultivos, setCultivos] = useState<number | null>(null);
  const [sensores, setSensores] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      listarCampos(1, 1).then(r => r.pagination.total).catch(() => null),
      listarCultivos(1, 1).then(r => r.pagination.total).catch(() => null),
      listarSensores().then(r => r.length).catch(() => null),
    ]).then(([c, cu, s]) => {
      setCampos(c);
      setCultivos(cu);
      setSensores(s);
    }).finally(() => setLoading(false));
  }, []);

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
        <DashboardCard title="Campos" value={loading ? "—" : String(campos ?? "—")} icon="🌾" />
        <DashboardCard title="Cultivos" value={loading ? "—" : String(cultivos ?? "—")} icon="🌱" />
        <DashboardCard title="Alertas activas" value="—" icon="⚠️" />
        <DashboardCard title="Sensores" value={loading ? "—" : String(sensores ?? "—")} icon="📡" />
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
