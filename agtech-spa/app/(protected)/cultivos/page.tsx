"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarCultivos } from "@/lib/services/cultivos";
import { Cultivo } from "@/lib/types";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function CultivosListPage() {
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listarCultivos()
      .then((res) => setCultivos(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Cultivos</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Catálogo de cultivos y constantes agronómicas
          </p>
        </div>
        <Link href="/cultivos/crear">
          <Button>+ Nuevo cultivo</Button>
        </Link>
      </div>

      <Card title="Catálogo">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Cultivo", accessor: (c: Cultivo) => c.nombreCultivo },
              { header: "Umbral humedad mínima", accessor: (c: Cultivo) => `${c.umbralHumedadMinima}%` },
            ]}
            data={cultivos}
            keyExtractor={(c) => c.nombreCultivo}
            emptyMessage="No hay cultivos registrados."
          />
        )}
      </Card>
    </div>
  );
}
