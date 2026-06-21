"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { crearParcela, listarParcelas } from "@/lib/services/parcelas";
import { listarCampos } from "@/lib/services/campos";
import { listarCultivos } from "@/lib/services/cultivos";
import { Cultivo } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button, Input } from "@/components/ui";
import type { ExistingPolygon } from "@/components/map/MapSelector";

const MapSelector = dynamic(
  () => import("@/components/map/MapSelector").then((m) => m.MapSelector),
  { ssr: false }
);

export default function CrearParcelaPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polygon, setPolygon] = useState<string | null>(null);
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [nombreParcela, setNombreParcela] = useState("");
  const [descripcionParcela, setDescripcionParcela] = useState("");
  const [selectedCultivoKey, setSelectedCultivoKey] = useState("");
  const [existingPolygons, setExistingPolygons] = useState<ExistingPolygon[]>([]);

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  useEffect(() => {
    listarCultivos()
      .then((res) => setCultivos(res.data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    listarCampos(1, 100).then((res) => {
      const campo = res.data.find((c) => c.nombreCampo === nombreCampo);
      if (!campo) return;
      const polygons: ExistingPolygon[] = [
        { geojson: campo.coordenadasCampo, label: campo.nombreCampo, color: "#666666", fillOpacity: 0.05 },
      ];
      listarParcelas(nombreCampo).then((res) => {
        res.data.forEach((p) => {
          polygons.push({ geojson: p.coordenadasParcela, label: p.nombreParcela, color: "#e67e22", fillOpacity: 0.2 });
        });
        setExistingPolygons(polygons);
      });
    }).catch(() => {});
  }, [nombreCampo]);

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
      const [cultivoNombre, cultivoVariedad] = selectedCultivoKey.split("|");
      await crearParcela(nombreCampo, {
        nombreParcela: nombreParcela.trim(),
        descripcionParcela: descripcionParcela.trim() || undefined,
        coordenadasParcela: polygon,
        nombreCultivo: cultivoNombre || undefined,
        variedad: cultivoVariedad || undefined,
      });
      router.push(`/campos/${encodeURIComponent(nombreCampo)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la parcela.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!puedeEditar(user)) return null;

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nueva parcela
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
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
              value={selectedCultivoKey}
              onChange={(e) => setSelectedCultivoKey(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                fontSize: "1rem",
                background: "var(--bg-input)",
              }}
            >
              <option value="">Sin cultivo asignado</option>
              {cultivos.map((c) => (
                <option key={`${c.nombreCultivo}|${c.variedad}`} value={`${c.nombreCultivo}|${c.variedad}`}>
                  {c.nombreCultivo} - {c.variedad}
                </option>
              ))}
            </select>
          </label>

          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>
              Perímetro de la parcela
            </span>
            <MapSelector onPolygonChange={setPolygon} existingPolygons={existingPolygons} />
            {polygon && (
              <span style={{ fontSize: "0.8rem", color: "var(--success)", marginTop: "0.3rem", display: "block" }}>
                ✅ Polígono definido
              </span>
            )}
          </div>

          {error && (
            <div style={{ color: "var(--danger)", fontSize: "0.9rem", background: "var(--danger-bg)", padding: "0.6rem", borderRadius: "var(--radius)" }}>
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
