"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { crearCultivo } from "@/lib/services/cultivos";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button } from "@/components/ui";

export default function CrearCultivoPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nombreCultivo, setNombreCultivo] = useState("");
  const [variedad, setVariedad] = useState("");

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nombreCultivo.trim() || !variedad.trim()) {
      setError("Completá el nombre del cultivo y la variedad.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await crearCultivo({ nombreCultivo: nombreCultivo.trim(), variedad: variedad.trim() });
      router.push("/cultivos");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el cultivo.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!puedeEditar(user)) return null;

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nuevo cultivo
      </h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
        Ingresá el nombre del cultivo y la variedad
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Cultivo</span>
            <input
              type="text"
              value={nombreCultivo}
              onChange={(e) => setNombreCultivo(e.target.value)}
              placeholder="Ej: Trigo, Maíz, Soja..."
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                fontSize: "1rem",
                background: "var(--bg-input)",
              }}
              required
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Variedad</span>
            <input
              type="text"
              value={variedad}
              onChange={(e) => setVariedad(e.target.value)}
              placeholder="Ej: ACA 303, DK 390, NS 4611..."
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                fontSize: "1rem",
                background: "var(--bg-input)",
              }}
              required
            />
          </label>

          {error && (
            <div style={{ color: "var(--danger)", fontSize: "0.9rem", background: "var(--danger-bg)", padding: "0.6rem", borderRadius: "var(--radius)" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting} disabled={!nombreCultivo.trim() || !variedad.trim()}>
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
