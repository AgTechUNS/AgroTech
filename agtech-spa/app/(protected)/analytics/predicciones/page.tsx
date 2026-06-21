"use client";

import { useEffect, useState } from "react";
import { obtenerPredicciones } from "@/lib/services/analytics";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas } from "@/lib/services/parcelas";
import { Prediccion, Campo, Parcela } from "@/lib/types";
import { Card, Button, Spinner } from "@/components/ui";

export default function PrediccionesPage() {
  const [data, setData] = useState<Prediccion[]>([]);
  const [campos, setCampos] = useState<Campo[]>([]);
  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [campoSeleccionado, setCampoSeleccionado] = useState("");
  const [parcelaSeleccionada, setParcelaSeleccionada] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listarCampos(1, 100).then((r) => setCampos(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!campoSeleccionado) return;
    listarParcelas(campoSeleccionado).then((r) => setParcelas(r.data)).catch(() => {});
  }, [campoSeleccionado]);

  function cargar() {
    if (!campoSeleccionado || !parcelaSeleccionada) return;
    setLoading(true);
    obtenerPredicciones(campoSeleccionado, parcelaSeleccionada)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Predicciones a corto plazo</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Pronóstico estimado para los próximos días
      </p>

      <Card style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Campo</label>
            <select value={campoSeleccionado} onChange={(e) => { setCampoSeleccionado(e.target.value); setParcelaSeleccionada(""); }}
              style={{ padding: "0.4rem 0.75rem", borderRadius: "var(--radius)", border: "1px solid var(--border)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }}>
              <option value="">Seleccionar campo</option>
              {campos.map((c) => <option key={c.nombreCampo} value={c.nombreCampo}>{c.nombreCampo}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Parcela</label>
            <select value={parcelaSeleccionada} onChange={(e) => setParcelaSeleccionada(e.target.value)}
              disabled={!campoSeleccionado}
              style={{ padding: "0.4rem 0.75rem", borderRadius: "var(--radius)", border: "1px solid var(--border)", fontSize: "0.9rem", background: !campoSeleccionado ? "var(--bg-glass)" : "var(--bg-input)", color: "var(--text-primary)" }}>
              <option value="">Seleccionar parcela</option>
              {parcelas.map((p) => <option key={p.nombreParcela} value={p.nombreParcela}>{p.nombreParcela}</option>)}
            </select>
          </div>
          <Button onClick={cargar} disabled={!parcelaSeleccionada}>Consultar</Button>
        </div>
      </Card>

      {loading ? <Spinner /> : data.length > 0 && (
        <Card title="Pronóstico">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {data.map((p, i) => (
              <div key={i} style={{
                padding: "0.75rem 1rem",
                borderRadius: "var(--radius)",
                background: "var(--bg-glass)",
                borderLeft: "4px solid var(--accent, #3b82f6)",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  <span>Emitido: {new Date(p.fechaEmision).toLocaleString()}</span>
                  <span>Válido: {new Date(p.fechaIni).toLocaleDateString()} – {new Date(p.fechaFin).toLocaleDateString()}</span>
                </div>
                <p style={{ margin: 0, fontSize: "0.9rem" }}>{p.resultado}</p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
