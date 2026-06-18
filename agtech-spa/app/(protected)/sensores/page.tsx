"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarSensores } from "@/lib/services/sensores";
import { Sensor } from "@/lib/types";
import { Card, Table, Spinner } from "@/components/ui";

const TIPO_LABEL: Record<string, string> = {
  temperatura_humedad: "Temp. / Humedad",
  ph: "pH de suelo",
  lluvia: "Precipitación",
};

export default function SensoresPage() {
  const [sensores, setSensores] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listarSensores()
      .then(setSensores)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Sensores</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Dispositivos IoT registrados en el LNS Console
          </p>
        </div>
      </div>

      <Card title="Listado de sensores">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              {
                header: "Device ID",
                accessor: (s: Sensor) => (
                  <Link
                    href={`/campos/${encodeURIComponent(s.nombreCampo)}/${encodeURIComponent(s.nombreParcela)}`}
                    style={{ color: "#2c7be5", textDecoration: "none", fontFamily: "monospace" }}
                  >
                    {s.deviceId}
                  </Link>
                ),
              },
              { header: "Campo", accessor: (s: Sensor) => s.nombreCampo },
              { header: "Parcela", accessor: (s: Sensor) => s.nombreParcela },
              { header: "Tipo", accessor: (s: Sensor) => TIPO_LABEL[s.tipo] ?? s.tipo },
              {
                header: "Estado",
                accessor: (s: Sensor) =>
                  s.activo
                    ? <span style={{ color: "#16a34a", fontWeight: 600 }}>Activo</span>
                    : <span style={{ color: "#94a3b8" }}>Inactivo</span>,
              },
            ]}
            data={sensores}
            keyExtractor={(s) => s.deviceId}
            emptyMessage="No hay sensores registrados. Configuralos desde el LNS Console."
          />
        )}
      </Card>
    </div>
  );
}
