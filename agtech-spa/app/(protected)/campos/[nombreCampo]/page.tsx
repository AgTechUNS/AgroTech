"use client";

import { useEffect, useState, ReactNode, Dispatch, SetStateAction } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { listarCampos, eliminarCampo } from "@/lib/services/campos";
import { listarParcelas, eliminarParcela } from "@/lib/services/parcelas";
import { listarSensores } from "@/lib/services/sensores";
import { listarReglas, editarRegla, eliminarRegla } from "@/lib/services/reglas";
import { Campo, Parcela, Sensor, Regla } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

const FieldsMap = dynamic(
  () => import("@/components/map/FieldsMap").then((m) => m.FieldsMap),
  { ssr: false }
);

export default function CampoDetallePage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);
  const [campo, setCampo] = useState<Campo | null>(null);
  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [sensores, setSensores] = useState<Sensor[]>([]);
  const [reglas, setReglas] = useState<Regla[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listarCampos(1, 100).then((res) =>
        res.data.find((c) => c.nombreCampo === nombreCampo) ?? null
      ),
      listarParcelas(nombreCampo).then((res) => res.data),
      listarSensores(),
      listarReglas(1, 50, nombreCampo).then((res) => res.data),
    ])
      .then(([c, p, s, r]) => {
        setCampo(c);
        setParcelas(p);
        setSensores(s.filter((sen) => sen.nombreCampo === nombreCampo));
        setReglas(r);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [nombreCampo]);

  if (loading) return <Spinner />;

  if (!campo) {
    return (
      <Card>
        <p>Campo no encontrado.</p>
        <Button onClick={() => router.push("/campos")}>Volver</Button>
      </Card>
    );
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>{campo.nombreCampo}</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            {campo.descripcionCampo ?? "Sin descripción"}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {puedeEditar(user) && (
            <>
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/editar`}>
                <Button variant="ghost">Editar</Button>
              </Link>
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/parcelas/crear`}>
                <Button>+ Nueva parcela</Button>
              </Link>
              <Button
                variant="ghost"
                style={{ color: "#e74c3c" }}
                onClick={async () => {
                  if (!window.confirm(`¿Eliminar "${campo.nombreCampo}" y sus parcelas?`)) return;
                  try {
                    await eliminarCampo(campo.nombreCampo);
                    router.push("/campos");
                  } catch { }
                }}
              >
                Eliminar
              </Button>
            </>
          )}
          <Button variant="ghost" onClick={() => router.push("/campos")}>
            Volver
          </Button>
        </div>
      </div>

      <Card style={{ padding: "0.5rem", marginBottom: "1.5rem" }}>
        <FieldsMap fields={[campo]} parcels={parcelas} sensores={sensores} height={400} />
      </Card>

      <Card title={`Parcelas (${parcelas.length})`}>
        <Table
          columns={[
            { header: "Parcela", accessor: (p: Parcela) => (
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(p.nombreParcela)}`} style={{ color: "#2c7be5", textDecoration: "none" }}>
                {p.nombreParcela}
              </Link>
            )},
            { header: "Cultivo", accessor: (p: Parcela) => p.nombreCultivo ? `${p.nombreCultivo} — ${p.variedad}` : "—" },
            { header: "Descripción", accessor: (p: Parcela) => p.descripcionParcela ?? "—" },
            ...(puedeEditar(user) ? accionesColumnsParcelas(nombreCampo, setParcelas) : []),
          ]}
          data={parcelas}
          keyExtractor={(p) => p.nombreParcela}
          emptyMessage="Este campo no tiene parcelas aún."
        />
      </Card>

      <Card title={`Reglas (${reglas.length})`} style={{ marginTop: "1.5rem" }}>
        <Table
          columns={[
            { header: "Nombre", accessor: (r: Regla) => r.nombre },
            { header: "Fórmula", accessor: (r: Regla) => <code style={{ background: "#f1f5f9", padding: "0.15rem 0.4rem", borderRadius: "4px", fontSize: "0.85rem" }}>{r.formula}</code> },
            {
              header: "Estado",
              accessor: (r: Regla) => (
                <button
                  onClick={async () => {
                    if (!puedeEditar(user)) return;
                    try {
                      await editarRegla(r.id, { habilitada: !r.habilitada });
                      setReglas((prev) => prev.map((x) => x.id === r.id ? { ...x, habilitada: !x.habilitada } : x));
                    } catch { }
                  }}
                  style={{
                    background: r.habilitada ? "#16a34a" : "#94a3b8",
                    color: "#fff",
                    border: "none",
                    borderRadius: "12px",
                    padding: "0.2rem 0.8rem",
                    fontSize: "0.8rem",
                    cursor: puedeEditar(user) ? "pointer" : "default",
                    fontWeight: 600,
                  }}
                >
                  {r.habilitada ? "Activa" : "Inactiva"}
                </button>
              ),
            },
            ...(puedeEditar(user) ? accionesColumnsReglasDetail(setReglas) : []),
          ]}
          data={reglas}
          keyExtractor={(r) => r.id}
          emptyMessage="No hay reglas asignadas a este campo."
        />
        {puedeEditar(user) && (
          <div style={{ marginTop: "0.8rem" }}>
            <Link href={`/reglas/crear`}>
              <Button variant="ghost">+ Asignar nueva regla</Button>
            </Link>
          </div>
        )}
      </Card>

      <Card title={`Sensores (${sensores.length})`} style={{ marginTop: "1.5rem" }}>
        <Table
          columns={[
            { header: "Device ID", accessor: (s: Sensor) => (
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(s.nombreParcela)}`} style={{ color: "#2c7be5", textDecoration: "none", fontFamily: "monospace" }}>
                {s.deviceId}
              </Link>
            )},
            { header: "Parcela", accessor: (s: Sensor) => s.nombreParcela },
            { header: "Tipo", accessor: (s: Sensor) => s.tipo === "temperatura_humedad" ? "Temp. / Humedad" : s.tipo === "ph" ? "pH" : s.tipo },
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
          emptyMessage="No hay sensores en este campo. Configuralos desde el LNS Console."
        />
      </Card>
    </div>
  );
}

function accionesColumnsParcelas(
  nombreCampo: string,
  setParcelas: Dispatch<SetStateAction<Parcela[]>>
): { header: string; accessor: (p: Parcela) => ReactNode }[] {
  return [{
    header: "Acciones",
    accessor: (p: Parcela) => (
      <div style={{ display: "flex", gap: "0.4rem" }}>
        <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(p.nombreParcela)}/editar`}>
          <Button variant="ghost" style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem" }}>Editar</Button>
        </Link>
        <Button
          variant="ghost"
          style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem", color: "#e74c3c" }}
          onClick={async () => {
            if (!window.confirm(`¿Eliminar "${p.nombreParcela}"?`)) return;
            try {
              await eliminarParcela(nombreCampo, p.nombreParcela);
              setParcelas((prev) => prev.filter((x) => x.nombreParcela !== p.nombreParcela));
            } catch { }
          }}
        >
          Eliminar
        </Button>
      </div>
    ),
  }];
}

function accionesColumnsReglasDetail(
  setReglas: Dispatch<SetStateAction<Regla[]>>
): { header: string; accessor: (r: Regla) => ReactNode }[] {
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
