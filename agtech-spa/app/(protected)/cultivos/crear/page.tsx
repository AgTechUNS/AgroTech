"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { crearCultivo, listarCatalogoCultivos } from "@/lib/services/cultivos";
import { CatalogoCultivo } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button } from "@/components/ui";

export default function CrearCultivoPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [catalogo, setCatalogo] = useState<CatalogoCultivo[]>([]);
  const [selectedCrop, setSelectedCrop] = useState("");
  const [selectedVariety, setSelectedVariety] = useState("");

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  useEffect(() => {
    listarCatalogoCultivos()
      .then(setCatalogo)
      .catch(() => setError("Error al cargar el catálogo"));
  }, []);

  const cropNames = Array.from(new Set(catalogo.map((c) => c.nombreCultivo))).sort();
  const availableVarieties = catalogo.filter((c) => c.nombreCultivo === selectedCrop);
  const selectedEntry = catalogo.find(
    (c) => c.nombreCultivo === selectedCrop && c.variedad === selectedVariety
  );

  function handleCropChange(crop: string) {
    setSelectedCrop(crop);
    setSelectedVariety("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedEntry) {
      setError("Seleccioná un cultivo y una variedad.");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await crearCultivo({
        nombreCultivo: selectedEntry.nombreCultivo,
        variedad: selectedEntry.variedad,
      });
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
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Seleccioná un cultivo del catálogo y su variedad
      </p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Cultivo</span>
            <select
              value={selectedCrop}
              onChange={(e) => handleCropChange(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "1rem",
                background: "#fff",
              }}
              required
            >
              <option value="">Seleccioná un cultivo</option>
              {cropNames.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Variedad</span>
            <select
              value={selectedVariety}
              onChange={(e) => setSelectedVariety(e.target.value)}
              disabled={!selectedCrop}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "6px",
                border: "1px solid #ccc",
                fontSize: "1rem",
                background: !selectedCrop ? "#f5f5f5" : "#fff",
              }}
              required
            >
              <option value="">Seleccioná una variedad</option>
              {availableVarieties.map((v) => (
                <option key={v.variedad} value={v.variedad}>
                  {v.variedad}
                </option>
              ))}
            </select>
          </label>

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting} disabled={!selectedEntry}>
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
