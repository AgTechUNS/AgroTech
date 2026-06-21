"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas, eliminarParcela } from "@/lib/services/parcelas";
import { listarSensores, listarLecturas } from "@/lib/services/sensores";
import { obtenerSatelital } from "@/lib/services/external";
import { Campo, Parcela, Sensor, Lectura } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button, Spinner } from "@/components/ui";
import { SensorCard } from "@/components/sensors/SensorCard";
import { SensorChart } from "@/components/sensors/SensorChart";

const FieldsMap = dynamic(
  () => import("@/components/map/FieldsMap").then((m) => m.FieldsMap),
  { ssr: false }
);

export default function ParcelaDetallePage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);
  const nombreParcela = decodeURIComponent(params.nombreParcela as string);
  const [campo, setCampo] = useState<Campo | null>(null);
  const [parcela, setParcela] = useState<Parcela | null>(null);
  const [sensores, setSensores] = useState<Sensor[]>([]);
  const [lecturas, setLecturas] = useState<Lectura[]>([]);
  const [loading, setLoading] = useState(true);
  const [ndviData, setNdviData] = useState<Record<string, number>>({});
  const [satelitalError, setSatelitalError] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listarCampos(1, 100).then((res) =>
        res.data.find((c) => c.nombreCampo === nombreCampo) ?? null
      ),
      listarParcelas(nombreCampo).then((res) =>
        res.data.find((p) => p.nombreParcela === nombreParcela) ?? null
      ),
      listarSensores(),
    ])
      .then(([c, p, s]) => {
        setCampo(c);
        setParcela(p);
        setSensores(s.filter((sen) => sen.nombreCampo === nombreCampo && sen.nombreParcela === nombreParcela));
        if (p) {
          obtenerSatelital(p.coordenadasParcela)
            .then((data) => setNdviData({ [p.nombreParcela]: data.ndvi, [c?.nombreCampo ?? ""]: data.ndvi }))
            .catch(() => setSatelitalError(true));
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [nombreCampo, nombreParcela]);

  useEffect(() => {
    const fetchLecturas = () => {
      listarLecturas(nombreCampo, nombreParcela).then(setLecturas).catch(() => {});
    };
    fetchLecturas();
    const interval = setInterval(fetchLecturas, 5000);
    return () => clearInterval(interval);
  }, [nombreCampo, nombreParcela]);

  if (loading) return <Spinner />;

  if (!parcela) {
    return (
      <Card>
        <p>Parcela no encontrada.</p>
        <Button onClick={() => router.push(`/campos/${encodeURIComponent(nombreCampo)}`)}>Volver</Button>
      </Card>
    );
  }

  const activos = sensores.filter((s) => s.activo);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>{nombreParcela}</h1>
          <p style={{ color: "var(--text-secondary)", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            {campo?.nombreCampo} — {parcela.nombreCultivo ? `${parcela.nombreCultivo} (${parcela.variedad})` : "Sin cultivo"}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {puedeEditar(user) && (
            <>
              <Link href={`/campos/${encodeURIComponent(nombreCampo)}/${encodeURIComponent(nombreParcela)}/editar`}>
                <Button variant="ghost">Editar</Button>
              </Link>
              <Button
                variant="ghost"
                style={{ color: "var(--danger)" }}
                onClick={async () => {
                  if (!window.confirm(`¿Eliminar "${nombreParcela}"?`)) return;
                  try {
                    await eliminarParcela(nombreCampo, nombreParcela);
                    router.push(`/campos/${encodeURIComponent(nombreCampo)}`);
                  } catch { }
                }}
              >
                Eliminar
              </Button>
            </>
          )}
          <Button onClick={() => router.push(`/campos/${encodeURIComponent(nombreCampo)}`)}>
            Volver al campo
          </Button>
        </div>
      </div>

      <Card style={{ padding: "0.5rem", marginBottom: "1.5rem" }}>
        {campo && <FieldsMap fields={[campo]} parcels={[parcela]} sensores={sensores} lecturas={lecturas} height={300} />}
      </Card>
      {ndviData[nombreParcela] !== undefined && (
        <Card style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <span style={{ fontSize: "1.5rem" }}>🌿</span>
            <div>
              <p style={{ margin: 0, fontWeight: 600 }}>NDVI: {ndviData[nombreParcela].toFixed(3)}</p>
              <p style={{ margin: "0.2rem 0 0", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                Índice de vegetación de diferencia normalizada — {ndviData[nombreParcela] >= 0.7 ? "Vegetación muy saludable" : ndviData[nombreParcela] >= 0.5 ? "Vegetación moderada" : ndviData[nombreParcela] >= 0.3 ? "Vegetación escasa" : "Suelo desnudo / estrés severo"}
              </p>
            </div>
          </div>
        </Card>
      )}
      {satelitalError && (
        <Card style={{ marginBottom: "1.5rem" }}>
          <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.85rem" }}>
            ⚠️ No se pudieron obtener datos satelitales. Mostrando colores por defecto en el mapa.
          </p>
        </Card>
      )}

      <Card title={`Sensores (${activos.length} activos)`} style={{ marginBottom: "1.5rem" }}>
        {activos.length === 0 ? (
          <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "1rem" }}>
            No hay sensores activos en esta parcela.
          </p>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem" }}>
            {activos.map((sensor) => {
              const ultima = [...lecturas].reverse().find((l) => l.sensorId === sensor.deviceId);
              return (
                <SensorCard
                  key={sensor.deviceId}
                  sensor={sensor}
                  ultimaTemp={ultima?.temperatura ?? undefined}
                  ultimaHum={ultima?.humedad ?? undefined}
                />
              );
            })}
          </div>
        )}
      </Card>

      {lecturas.length > 0 && (
        <Card title="Últimas lecturas">
          <SensorChart lecturas={lecturas} />
        </Card>
      )}
    </div>
  );
}
