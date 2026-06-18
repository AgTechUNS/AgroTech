"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { crearRegla } from "@/lib/services/reglas";
import { Card, Button, Input } from "@/components/ui";

const METRICAS = [
  { value: "temperatura", label: "Temperatura (°C)" },
  { value: "humedad_suelo", label: "Humedad del suelo (%)" },
  { value: "precipitacion", label: "Precipitación (mm)" },
  { value: "viento", label: "Viento (km/h)" },
  { value: "ndvi", label: "NDVI" },
];

const OPERADORES = [
  { value: ">=", label: "Mayor o igual (≥)" },
  { value: "<=", label: "Menor o igual (≤)" },
  { value: ">", label: "Mayor (>)" },
  { value: "<", label: "Menor (<)" },
  { value: "==", label: "Igual (=)" },
];

export default function CrearReglaPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metrica, setMetrica] = useState(METRICAS[0].value);
  const [operador, setOperador] = useState(OPERADORES[0].value);
  const [valorStr, setValorStr] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const valor = parseFloat(valorStr);
    if (isNaN(valor)) {
      setError("El valor umbral debe ser un número.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await crearRegla({ metrica, operador, valor });
      router.push("/reglas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la regla.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nueva regla agroclimática
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Definí un umbral de evaluación para el pipeline de alertas
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Métrica</span>
            <select
              value={metrica}
              onChange={(e) => setMetrica(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "1rem",
                background: "#fff",
              }}
            >
              {METRICAS.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Operador</span>
            <select
              value={operador}
              onChange={(e) => setOperador(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "1rem",
                background: "#fff",
              }}
            >
              {OPERADORES.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </label>

          <Input
            label="Valor umbral"
            type="number"
            step="0.1"
            placeholder="Ej: 38.0"
            value={valorStr}
            onChange={(e) => setValorStr(e.target.value)}
            required
          />

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>
              Guardar regla
            </Button>
            <Button variant="ghost" onClick={() => router.push("/reglas")}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
