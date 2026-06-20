"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas } from "@/lib/services/parcelas";
import { listarSensores, listarLecturas } from "@/lib/services/sensores";
import { Campo, Parcela, Sensor, Lectura } from "@/lib/types";
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
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);
  const nombreParcela = decodeURIComponent(params.nombreParcela as string);
  const [campo, setCampo] = useState<Campo | null>(null);
  const [parcela, setParcela] = useState<Parcela | null>(null);
  const [sensores, setSensores] = useState<Sensor[]>([]);
  const [lecturas, setLecturas] = useState<Lectura[]>([]);
  const [loading, setLoading] = useState(true);

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
      listarLecturas(nombreCampo, nombreParcela),
    ])
      .then(([c, p, s, l]) => {
        setCampo(c);
        setParcela(p);
        setSensores(s.filter((sen) => sen.nombreCampo === nombreCampo && sen.nombreParcela === nombreParcela));
        setLecturas(l);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
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
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            {campo?.nombreCampo} — {parcela.nombreCultivo ?? "Sin cultivo"}
          </p>
        </div>
        <Button onClick={() => router.push(`/campos/${encodeURIComponent(nombreCampo)}`)}>
          Volver al campo
        </Button>
      </div>

      <Card style={{ padding: "0.5rem", marginBottom: "1.5rem" }}>
        {campo && <FieldsMap fields={[campo]} parcels={[parcela]} height={300} />}
      </Card>

      <Card title={`Sensores (${activos.length} activos)`} style={{ marginBottom: "1.5rem" }}>
        {activos.length === 0 ? (
          <p style={{ color: "#94a3b8", textAlign: "center", padding: "1rem" }}>
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
