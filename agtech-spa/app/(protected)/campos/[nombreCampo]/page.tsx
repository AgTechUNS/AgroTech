"use client";

import { useEffect, useState, ReactNode, Dispatch, SetStateAction } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { listarCampos, eliminarCampo } from "@/lib/services/campos";
import { listarParcelas, eliminarParcela } from "@/lib/services/parcelas";
import { listarSensores } from "@/lib/services/sensores";
import { listarReglas, editarRegla } from "@/lib/services/reglas";
import { Campo, Parcela, Sensor, Regla } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar, puedeCrearReglas } from "@/lib/auth/roles";
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
  const [todasReglas, setTodasReglas] = useState<Regla[]>([]);
  const [asignando, setAsignando] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listarCampos(1, 100).then((res) =>
        res.data.find((c) => c.nombreCampo === nombreCampo) ?? null
      ),
      listarParcelas(nombreCampo).then((res) => res.data),
      listarSensores(),
      listarReglas(),
    ])
      .then(([c, p, s, reglas]) => {
        setCampo(c);
        setParcelas(p);
        setSensores(s.filter((sen) => sen.nombreCampo === nombreCampo));
        setTodasReglas(reglas as Regla[]);
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
          <p style={{ color: "var(--text-secondary)", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
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
                style={{ color: "var(--danger)" }}
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
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(p.nombreParcela)}`} style={{ color: "var(--accent)", textDecoration: "none" }}>
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

      <Card title={`Sensores (${sensores.length})`} style={{ marginTop: "1.5rem" }}>
        <Table
          columns={[
            { header: "Device ID", accessor: (s: Sensor) => (
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(s.nombreParcela)}`} style={{ color: "var(--accent)", textDecoration: "none", fontFamily: "monospace" }}>
                {s.deviceId}
              </Link>
            )},
            { header: "Parcela", accessor: (s: Sensor) => s.nombreParcela },
            { header: "Tipo", accessor: (s: Sensor) => s.tipo === "temperatura_humedad" ? "Temp. / Humedad" : s.tipo === "ph" ? "pH" : s.tipo },
            {
              header: "Estado",
              accessor: (s: Sensor) =>
                s.activo
                  ? <span style={{ color: "var(--success)", fontWeight: 600 }}>Activo</span>
                  : <span style={{ color: "var(--text-muted)" }}>Inactivo</span>,
            },
          ]}
          data={sensores}
          keyExtractor={(s) => s.deviceId}
          emptyMessage="No hay sensores en este campo. Configuralos desde el LNS Console."
        />
      </Card>

      <Card title={`Reglas (${todasReglas.length})`} style={{ marginTop: "1.5rem" }}>
        <Table
          columns={[
            { header: "Nombre", accessor: (r: Regla) => r.nombre },
            { header: "Métrica", accessor: (r: Regla) => {
              const labels: Record<string, string> = { temperatura: "Temperatura", humedad_suelo: "Humedad suelo", precipitacion: "Precipitación", viento: "Viento", ndvi: "NDVI" };
              return labels[r.metrica] ?? r.metrica;
            }},
            { header: "Condición", accessor: (r: Regla) => `${r.operador} ${r.valor}` },
            ...(puedeCrearReglas(user) ? [{
              header: "Asignada",
              accessor: (r: Regla) => {
                const asignada = r.camposAsignados?.includes(nombreCampo) ?? false;
                const cargando = asignando === r.id;
                return (
                  <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", cursor: cargando ? "wait" : "pointer" }}>
                    <input
                      type="checkbox"
                      checked={asignada}
                      disabled={cargando}
                      onChange={async () => {
                        setAsignando(r.id);
                        try {
                          const nuevos = asignada
                            ? (r.camposAsignados ?? []).filter((c) => c !== nombreCampo)
                            : [...(r.camposAsignados ?? []), nombreCampo];
                          await editarRegla(r.id, { camposAsignados: nuevos });
                          setTodasReglas((prev) =>
                            prev.map((x) => x.id === r.id ? { ...x, camposAsignados: nuevos } : x)
                          );
                        } catch {}
                        setAsignando(null);
                      }}
                    />
                    {cargando ? "—" : asignada ? "Sí" : "No"}
                  </label>
                );
              },
            }] : []),
          ]}
          data={todasReglas}
          keyExtractor={(r) => r.id}
          emptyMessage="No hay reglas configuradas. Crealas desde la sección Reglas."
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
          style={{ fontSize: "0.8rem", padding: "0.2rem 0.6rem", color: "var(--danger)" }}
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


