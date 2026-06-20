"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { obtenerRegla, editarRegla } from "@/lib/services/reglas";
import { listarCampos } from "@/lib/services/campos";
import { Campo } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button, Input, Spinner } from "@/components/ui";

const METRICAS = [
  { value: "temperatura", label: "Temperatura" },
  { value: "humedad_suelo", label: "Humedad del suelo" },
  { value: "precipitacion", label: "Precipitación" },
  { value: "viento", label: "Viento" },
  { value: "ndvi", label: "NDVI" },
];

const OPERADORES = [
  { value: ">=", label: "≥ Mayor o igual" },
  { value: "<=", label: "≤ Menor o igual" },
  { value: ">", label: "> Mayor" },
  { value: "<", label: "< Menor" },
  { value: "==", label: "= Igual" },
];

const METRICA_UNITS: Record<string, string> = {
  temperatura: "°C",
  humedad_suelo: "%",
  precipitacion: "mm",
  viento: "km/h",
  ndvi: "",
};

const OP_SYMBOLS: Record<string, string> = {
  ">=": "≥", "<=": "≤", ">": ">", "<": "<", "==": "=",
};

export default function EditarReglaPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const id = params.id as string;

  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [campos, setCampos] = useState<Campo[]>([]);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [nombreCampo, setNombreCampo] = useState("");
  const [metrica, setMetrica] = useState(METRICAS[0].value);
  const [operador, setOperador] = useState(OPERADORES[0].value);
  const [umbralStr, setUmbralStr] = useState("");

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  useEffect(() => {
    Promise.all([
      obtenerRegla(id),
      listarCampos(1, 100),
    ])
      .then(([regla, resCampos]) => {
        setNombre(regla.nombre);
        setDescripcion(regla.descripcion);
        setNombreCampo(regla.nombreCampo);
        setMetrica(regla.metrica);
        setOperador(regla.operador);
        setUmbralStr(String(regla.umbral));
        setCampos(resCampos.data);
      })
      .catch(() => setError("Error al cargar la regla"))
      .finally(() => setLoading(false));
  }, [id]);

  const umbral = parseFloat(umbralStr);
  const formulaPreview = metrica && operador && !isNaN(umbral)
    ? `${metrica} ${OP_SYMBOLS[operador]} ${umbral}${METRICA_UNITS[metrica] ?? ""}`
    : null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nombre.trim()) { setError("El nombre es obligatorio."); return; }
    if (!nombreCampo) { setError("Seleccioná un campo."); return; }
    if (isNaN(umbral)) { setError("El umbral debe ser un número."); return; }

    setSubmitting(true);
    setError(null);
    try {
      await editarRegla(id, { nombre: nombre.trim(), descripcion: descripcion.trim(), metrica, operador, umbral, nombreCampo });
      router.push("/reglas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al editar la regla.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!puedeEditar(user)) return null;
  if (loading) return <Spinner />;

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Editar regla
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        {nombre}
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <Input
            label="Nombre de la regla"
            placeholder="Ej: Alerta de helada"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
          />

          <Input
            label="Descripción"
            placeholder="Ej: Detecta temperaturas peligrosamente bajas"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
          />

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Campo</span>
            <select
              value={nombreCampo}
              onChange={(e) => setNombreCampo(e.target.value)}
              style={{ padding: "0.5rem 0.75rem", borderRadius: "6px", border: "1px solid #ccc", fontSize: "1rem", background: "#fff" }}
              required
            >
              <option value="">Seleccioná un campo</option>
              {campos.map((c) => (
                <option key={c.nombreCampo} value={c.nombreCampo}>{c.nombreCampo}</option>
              ))}
            </select>
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Métrica</span>
            <select
              value={metrica}
              onChange={(e) => setMetrica(e.target.value)}
              style={{ padding: "0.5rem 0.75rem", borderRadius: "6px", border: "1px solid #ccc", fontSize: "1rem", background: "#fff" }}
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
              style={{ padding: "0.5rem 0.75rem", borderRadius: "6px", border: "1px solid #ccc", fontSize: "1rem", background: "#fff" }}
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
            placeholder="Ej: 2.0"
            value={umbralStr}
            onChange={(e) => setUmbralStr(e.target.value)}
            required
          />

          {formulaPreview && (
            <div style={{ background: "#f0f9f0", padding: "0.6rem 0.8rem", borderRadius: "6px", fontSize: "0.9rem", color: "#2e7d32" }}>
              Fórmula: <code style={{ background: "#dcedc8", padding: "0.15rem 0.4rem", borderRadius: "4px" }}>{formulaPreview}</code>
            </div>
          )}

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>
              Guardar cambios
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
