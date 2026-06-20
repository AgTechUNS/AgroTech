"use client";

import { useEffect, useState, ReactNode, Dispatch, SetStateAction } from "react";
import Link from "next/link";
import { listarReglas, editarRegla, eliminarRegla } from "@/lib/services/reglas";
import { listarCampos } from "@/lib/services/campos";
import { Regla, Campo } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function ReglasListPage() {
  const { user } = useAuthContext();
  const [reglas, setReglas] = useState<Regla[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroCampo, setFiltroCampo] = useState("");
  const [campos, setCampos] = useState<Campo[]>([]);

  function cargarReglas() {
    setLoading(true);
    listarReglas(1, 50, filtroCampo || undefined)
      .then((res) => setReglas(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    cargarReglas();
    listarCampos(1, 100).then((res) => setCampos(res.data)).catch(() => {});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroCampo]);

  async function toggleHabilitada(regla: Regla) {
    try {
      await editarRegla(regla.id, { habilitada: !regla.habilitada });
      setReglas((prev) => prev.map((r) => r.id === regla.id ? { ...r, habilitada: !r.habilitada } : r));
    } catch { }
  }

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
        {campos.length > 0 && (
          <div style={{ marginBottom: "1rem" }}>
            <select
              value={filtroCampo}
              onChange={(e) => setFiltroCampo(e.target.value)}
              style={{
                padding: "0.4rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "0.9rem",
                background: "#fff",
              }}
            >
              <option value="">Todos los campos</option>
              {campos.map((c) => (
                <option key={c.nombreCampo} value={c.nombreCampo}>{c.nombreCampo}</option>
              ))}
            </select>
          </div>
        )}

        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Nombre", accessor: (r: Regla) => r.nombre },
              { header: "Campo", accessor: (r: Regla) => r.nombreCampo },
              { header: "Fórmula", accessor: (r: Regla) => <code style={{ background: "#f1f5f9", padding: "0.15rem 0.4rem", borderRadius: "4px", fontSize: "0.85rem" }}>{r.formula}</code> },
              {
                header: "Estado",
                accessor: (r: Regla) => (
                  <button
                    onClick={() => toggleHabilitada(r)}
                    style={{
                      background: r.habilitada ? "#16a34a" : "#94a3b8",
                      color: "#fff",
                      border: "none",
                      borderRadius: "12px",
                      padding: "0.2rem 0.8rem",
                      fontSize: "0.8rem",
                      cursor: "pointer",
                      fontWeight: 600,
                    }}
                  >
                    {r.habilitada ? "Activa" : "Inactiva"}
                  </button>
                ),
              },
              ...(puedeEditar(user) ? accionesColumnsReglas(setReglas) : []),
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

function accionesColumnsReglas(setReglas: Dispatch<SetStateAction<Regla[]>>): { header: string; accessor: (r: Regla) => ReactNode }[] {
  return [{
    header: "Acciones",
    accessor: (r: Regla) => (
      <div style={{ display: "flex", gap: "0.4rem" }}>
        <Link href={`/reglas/${encodeURIComponent(r.id)}/editar`}>
          <Button variant="ghost" style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem" }}>Editar</Button>
        </Link>
        <Button
          variant="ghost"
          style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem", color: "#e74c3c" }}
          onClick={async () => {
            if (!window.confirm(`¿Eliminar la regla "${r.nombre}"?`)) return;
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
  }];
}
