"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarReglas, eliminarRegla } from "@/lib/services/reglas";
import { Regla } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeCrearReglas } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function ReglasListPage() {
  const { user } = useAuthContext();
  const [reglas, setReglas] = useState<Regla[]>([]);
  const [loading, setLoading] = useState(true);

  function cargar() {
    setLoading(true);
    listarReglas()
      .then(setReglas)
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { cargar(); }, []);

  const METRICA_LABELS: Record<string, string> = {
    temperatura: "Temperatura",
    humedad_suelo: "Humedad suelo",
    precipitacion: "Precipitación",
    viento: "Viento",
    ndvi: "NDVI",
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Reglas agroclimáticas</h1>
          <p style={{ color: "var(--text-secondary)", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Umbrales globales asignables a los campos
          </p>
        </div>
        {puedeCrearReglas(user) && (
          <Link href="/reglas/crear">
            <Button>+ Nueva regla</Button>
          </Link>
        )}
      </div>

      <Card title={`Reglas (${reglas.length})`}>
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Nombre", accessor: (r: Regla) => r.nombre },
              { header: "Métrica", accessor: (r: Regla) => METRICA_LABELS[r.metrica] ?? r.metrica },
              { header: "Operador", accessor: (r: Regla) => r.operador },
              { header: "Valor", accessor: (r: Regla) => r.valor },
              { header: "Campos asignados", accessor: (r: Regla) => r.camposAsignados && r.camposAsignados.length > 0 ? r.camposAsignados.join(", ") : "—" },
              ...(puedeCrearReglas(user) ? [{
                header: "Acciones",
                accessor: (r: Regla) => (
                  <div style={{ display: "flex", gap: "0.4rem" }}>
                    <Link href={`/reglas/${encodeURIComponent(r.id)}/editar`}>
                      <Button variant="ghost" style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem" }}>Editar</Button>
                    </Link>
                    <Button
                      variant="ghost"
                      style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem", color: "var(--danger)" }}
                      onClick={async () => {
                        if (!window.confirm(`¿Eliminar "${r.nombre}"?`)) return;
                        try {
                          await eliminarRegla(r.id);
                          setReglas((prev) => prev.filter((x) => x.id !== r.id));
                        } catch { }
                      }}
                    >
                      Eliminar
                    </Button>
                  </div>
                ),
              }] : []),
            ]}
            data={reglas}
            keyExtractor={(r) => r.id}
            emptyMessage="No hay reglas configuradas."
          />
        )}
      </Card>
    </div>
  );
}
