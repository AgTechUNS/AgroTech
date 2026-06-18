"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { crearCultivo } from "@/lib/services/cultivos";
import { Card, Button, Input } from "@/components/ui";

export default function CrearCultivoPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nombreCultivo, setNombreCultivo] = useState("");
  const [umbralStr, setUmbralStr] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nombreCultivo.trim()) {
      setError("El nombre del cultivo es obligatorio.");
      return;
    }
    const umbral = parseFloat(umbralStr);
    if (isNaN(umbral) || umbral < 0) {
      setError("El umbral de humedad debe ser un número positivo.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await crearCultivo({ nombreCultivo: nombreCultivo.trim(), umbralHumedadMinima: umbral });
      router.push("/cultivos");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el cultivo.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nuevo cultivo
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Agregar un cultivo al catálogo con sus constantes agronómicas
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <Input
            label="Nombre del cultivo"
            placeholder="Ej: Trigo"
            value={nombreCultivo}
            onChange={(e) => setNombreCultivo(e.target.value)}
            required
          />

          <Input
            label="Umbral de humedad mínima (%)"
            type="number"
            step="0.1"
            placeholder="Ej: 30.5"
            value={umbralStr}
            onChange={(e) => setUmbralStr(e.target.value)}
            required
          />

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>
              Guardar cultivo
            </Button>
            <Button variant="ghost" onClick={() => router.push("/cultivos")}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
