"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { obtenerCampo, editarCampo } from "@/lib/services/campos";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button, Input, Spinner } from "@/components/ui";
import type { ExistingPolygon } from "@/components/map/MapSelector";

const MapSelector = dynamic(
  () => import("@/components/map/MapSelector").then((m) => m.MapSelector),
  { ssr: false }
);

export default function EditarCampoPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);

  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [polygon, setPolygon] = useState<string | null>(null);
  const [descripcion, setDescripcion] = useState("");
  const [existingPolygons, setExistingPolygons] = useState<ExistingPolygon[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  useEffect(() => {
    obtenerCampo(nombreCampo)
      .then((c) => {
        setDescripcion(c.descripcionCampo ?? "");
        setExistingPolygons([{ geojson: c.coordenadasCampo, label: c.nombreCampo, color: "#666", fillOpacity: 0.1 }]);
      })
      .catch(() => setError("Error al cargar el campo"))
      .finally(() => setLoading(false));
  }, [nombreCampo]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!polygon) {
      setError("Dibujá el perímetro del campo en el mapa.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await editarCampo(nombreCampo, {
        descripcionCampo: descripcion.trim() || undefined,
        coordenadasCampo: polygon,
      });
      router.push(`/campos/${encodeURIComponent(nombreCampo)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al editar el campo.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!puedeEditar(user)) return null;
  if (loading) return <Spinner />;

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Editar campo
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
        {nombreCampo}
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <Input
            label="Nombre del campo"
            value={nombreCampo}
            disabled
          />

          <Input
            label="Descripción (opcional)"
            placeholder="Ej: Establecimiento norte destinado a cultivos rotativos"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
          />

          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>
              Perímetro del campo (dibujá uno nuevo para actualizar)
            </span>
            <MapSelector onPolygonChange={setPolygon} existingPolygons={existingPolygons} />
            {polygon && (
              <span style={{ fontSize: "0.8rem", color: "var(--success)", marginTop: "0.3rem", display: "block" }}>
                ✅ Nuevo polígono definido
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
              Guardar cambios
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
