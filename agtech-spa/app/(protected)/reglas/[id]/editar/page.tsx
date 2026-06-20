"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { obtenerRegla, editarRegla } from "@/lib/services/reglas";
import { listarCampos } from "@/lib/services/campos";
import { Campo, Regla } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeCrearReglas } from "@/lib/auth/roles";
import { Card, Button, Spinner } from "@/components/ui";

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

export default function EditarReglaPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const id = decodeURIComponent(params.id as string);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [metrica, setMetrica] = useState(METRICAS[0].value);
  const [operador, setOperador] = useState(OPERADORES[0].value);
  const [valorStr, setValorStr] = useState("");
  const [campos, setCampos] = useState<Campo[]>([]);
  const [camposSeleccionados, setCamposSeleccionados] = useState<string[]>([]);

  useEffect(() => {
    if (!puedeCrearReglas(user)) { router.push("/dashboard"); return; }
    Promise.all([
      obtenerRegla(id),
      listarCampos(1, 100),
    ]).then(([regla, resCampos]) => {
      setNombre(regla.nombre);
      setDescripcion(regla.descripcion ?? "");
      setMetrica(regla.metrica);
      setOperador(regla.operador);
      setValorStr(String(regla.valor));
      setCamposSeleccionados(regla.camposAsignados ?? []);
      setCampos(resCampos.data);
    }).catch(() => router.push("/reglas"))
    .finally(() => setLoading(false));
  }, [id, user, router]);

  function toggleCampo(nombreCampo: string) {
    setCamposSeleccionados((prev) =>
      prev.includes(nombreCampo) ? prev.filter((c) => c !== nombreCampo) : [...prev, nombreCampo]
    );
  }

  if (!puedeCrearReglas(user)) return null;
  if (loading) return <Spinner />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const valor = parseFloat(valorStr);
    if (!nombre.trim()) { setError("El nombre es obligatorio."); return; }
    if (isNaN(valor)) { setError("El valor debe ser un número."); return; }

    setSubmitting(true);
    setError(null);
    try {
      await editarRegla(id, {
        nombre: nombre.trim(),
        descripcion: descripcion.trim() || undefined,
        metrica, operador, valor,
        camposAsignados: camposSeleccionados,
      });
      router.push("/reglas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al editar la regla.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Editar regla</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>{nombre}</p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem", maxWidth: 500 }}>
          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.3rem" }}>Nombre *</span>
            <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} required
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "1rem", boxSizing: "border-box", background: "var(--bg-input)", color: "var(--text-primary)" }} />
          </div>
          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.3rem" }}>Descripción</span>
            <input type="text" value={descripcion} onChange={(e) => setDescripcion(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "1rem", boxSizing: "border-box", background: "var(--bg-input)", color: "var(--text-primary)" }} />
          </div>
          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Métrica *</span>
            <select value={metrica} onChange={(e) => setMetrica(e.target.value)}
              style={{ padding: "0.5rem 0.75rem", borderRadius: "var(--radius)", border: "1px solid var(--border)", fontSize: "1rem", background: "var(--bg-input)", color: "var(--text-primary)" }}>
              {METRICAS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Operador *</span>
            <select value={operador} onChange={(e) => setOperador(e.target.value)}
              style={{ padding: "0.5rem 0.75rem", borderRadius: "var(--radius)", border: "1px solid var(--border)", fontSize: "1rem", background: "var(--bg-input)", color: "var(--text-primary)" }}>
              {OPERADORES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </label>
          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.3rem" }}>Valor umbral *</span>
            <input type="number" step="0.1" value={valorStr} onChange={(e) => setValorStr(e.target.value)} required
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "1rem", boxSizing: "border-box", background: "var(--bg-input)", color: "var(--text-primary)" }} />
          </div>

          {campos.length > 0 && (
            <div>
              <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Asignar a campos</span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {campos.map((c) => {
                  const selected = camposSeleccionados.includes(c.nombreCampo);
                  return (
                    <label key={c.nombreCampo}
                      style={{
                        display: "flex", alignItems: "center", gap: "0.3rem",
                        padding: "0.3rem 0.6rem", borderRadius: "6px",
                        background: selected ? "var(--accent-bg)" : "var(--bg-glass)",
                        border: selected ? "1px solid var(--accent)" : "1px solid var(--border)",
                        cursor: "pointer", fontSize: "0.85rem",
                      }}>
                      <input type="checkbox" checked={selected} onChange={() => toggleCampo(c.nombreCampo)} />
                      {c.nombreCampo}
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {error && (
            <div style={{ color: "var(--danger)", fontSize: "0.9rem", background: "var(--danger-bg)", padding: "0.6rem", borderRadius: "var(--radius)" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>Guardar cambios</Button>
            <Button variant="ghost" onClick={() => router.push("/reglas")}>Cancelar</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
