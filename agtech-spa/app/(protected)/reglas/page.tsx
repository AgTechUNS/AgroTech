"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarReglas } from "@/lib/services/reglas";
import { Regla } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

const OPERADOR_LABELS: Record<string, string> = {
  ">=": "Mayor o igual",
  "<=": "Menor o igual",
  ">": "Mayor",
  "<": "Menor",
  "==": "Igual",
  "!=": "Distinto",
};

const METRICA_LABELS: Record<string, string> = {
  temperatura: "Temperatura (°C)",
  humedad_suelo: "Humedad del suelo (%)",
  precipitacion: "Precipitación (mm)",
  viento: "Viento (km/h)",
  ndvi: "NDVI",
};

export default function ReglasListPage() {
  const { user } = useAuthContext();
  const [reglas, setReglas] = useState<Regla[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listarReglas()
      .then((res) => setReglas(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Reglas agroclimáticas</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Umbrales de evaluación para el pipeline de alertas tempranas
          </p>
        </div>
        {puedeEditar(user) && (
          <Link href="/reglas/crear">
            <Button>+ Nueva regla</Button>
          </Link>
        )}
      </div>

      <Card title="Reglas configuradas">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Métrica", accessor: (r: Regla) => METRICA_LABELS[r.metrica] ?? r.metrica },
              { header: "Operador", accessor: (r: Regla) => OPERADOR_LABELS[r.operador] ?? r.operador },
              { header: "Valor umbral", accessor: (r: Regla) => r.valor },
            ]}
            data={reglas}
            keyExtractor={(r) => r.metrica + r.operador + r.valor}
            emptyMessage="No hay reglas configuradas."
          />
        )}
      </Card>
    </div>
  );
}
