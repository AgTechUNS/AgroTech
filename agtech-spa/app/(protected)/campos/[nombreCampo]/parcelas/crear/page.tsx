"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { crearParcela } from "@/lib/services/parcelas";
import { listarCultivos } from "@/lib/services/cultivos";
import { Cultivo } from "@/lib/types";
import { Card, Button, Input } from "@/components/ui";

const MapSelector = dynamic(
  () => import("@/components/map/MapSelector").then((m) => m.MapSelector),
  { ssr: false }
);

export default function CrearParcelaPage() {
  const params = useParams();
  const router = useRouter();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polygon, setPolygon] = useState<string | null>(null);
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);

  const [nombreParcela, setNombreParcela] = useState("");
  const [descripcionParcela, setDescripcionParcela] = useState("");
  const [nombreCultivo, setNombreCultivo] = useState("");

  useEffect(() => {
    listarCultivos()
      .then((res) => setCultivos(res.data))
      .catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nombreParcela.trim()) {
      setError("El nombre de la parcela es obligatorio.");
      return;
    }
    if (!polygon) {
      setError("Dibujá el perímetro de la parcela en el mapa.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await crearParcela(nombreCampo, {
        nombreParcela: nombreParcela.trim(),
        descripcionParcela: descripcionParcela.trim() || undefined,
        coordenadasParcela: polygon,
        nombreCultivo: nombreCultivo || undefined,
      });
      router.push(`/campos/${encodeURIComponent(nombreCampo)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la parcela.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nueva parcela
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Campo: <strong>{nombreCampo}</strong>
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <Input
            label="Nombre de la parcela"
            placeholder="Ej: Lote C"
            value={nombreParcela}
            onChange={(e) => setNombreParcela(e.target.value)}
            required
          />

          <Input
            label="Descripción (opcional)"
            placeholder="Ej: Parcela oeste con riego por aspersión"
            value={descripcionParcela}
            onChange={(e) => setDescripcionParcela(e.target.value)}
          />

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Cultivo (opcional)</span>
            <select
              value={nombreCultivo}
              onChange={(e) => setNombreCultivo(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "1rem",
                background: "#fff",
              }}
            >
              <option value="">Sin cultivo asignado</option>
              {cultivos.map((c) => (
                <option key={c.nombreCultivo} value={c.nombreCultivo}>
                  {c.nombreCultivo}
                </option>
              ))}
            </select>
          </label>

          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>
              Perímetro de la parcela
            </span>
            <MapSelector onPolygonChange={setPolygon} />
            {polygon && (
              <span style={{ fontSize: "0.8rem", color: "#27ae60", marginTop: "0.3rem", display: "block" }}>
                ✅ Polígono definido
              </span>
            )}
          </div>

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>
              Guardar parcela
            </Button>
            <Button variant="ghost" onClick={() => router.push(`/campos/${encodeURIComponent(nombreCampo)}`)}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
