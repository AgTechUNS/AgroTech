"use client";

import { useEffect, useState } from "react";
import { obtenerPredicciones } from "@/lib/services/analytics";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas } from "@/lib/services/parcelas";
import { Prediccion, Campo, Parcela } from "@/lib/types";
import { Card, Table, Button, Spinner } from "@/components/ui";

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

  function probLluviaColor(pct: number): string {
    if (pct >= 70) return "#dc2626";
    if (pct >= 40) return "#d97706";
    return "#16a34a";
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Predicciones a corto plazo</h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Pronóstico estimado para los próximos días
      </p>

      <Card style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Campo</label>
            <select value={campoSeleccionado} onChange={(e) => { setCampoSeleccionado(e.target.value); setParcelaSeleccionada(""); }}
              style={{ padding: "0.4rem 0.75rem", borderRadius: "6px", border: "1px solid #ccc", fontSize: "0.9rem", background: "#fff" }}>
              <option value="">Seleccionar campo</option>
              {campos.map((c) => <option key={c.nombreCampo} value={c.nombreCampo}>{c.nombreCampo}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Parcela</label>
            <select value={parcelaSeleccionada} onChange={(e) => setParcelaSeleccionada(e.target.value)}
              disabled={!campoSeleccionado}
              style={{ padding: "0.4rem 0.75rem", borderRadius: "6px", border: "1px solid #ccc", fontSize: "0.9rem", background: !campoSeleccionado ? "#f5f5f5" : "#fff" }}>
              <option value="">Seleccionar parcela</option>
              {parcelas.map((p) => <option key={p.nombreParcela} value={p.nombreParcela}>{p.nombreParcela}</option>)}
            </select>
          </div>
          <Button onClick={cargar} disabled={!parcelaSeleccionada}>Consultar</Button>
        </div>
      </Card>

      {loading ? <Spinner /> : data.length > 0 && (
        <Card title="Pronóstico diario">
          <Table
            columns={[
              { header: "Fecha", accessor: (p: Prediccion) => p.fecha },
              { header: "Temp. estimada", accessor: (p: Prediccion) => `${p.temperatura_estimada}°C` },
              { header: "Humedad estimada", accessor: (p: Prediccion) => `${p.humedad_estimada}%` },
              { header: "Prob. lluvia", accessor: (p: Prediccion) => (
                <span style={{ color: probLluviaColor(p.probabilidad_lluvia), fontWeight: 600 }}>
                  {p.probabilidad_lluvia}%
                </span>
              )},
            ]}
            data={data}
            keyExtractor={(p) => p.fecha}
            emptyMessage="No hay predicciones disponibles."
          />
        </Card>
      )}
    </div>
  );
}
