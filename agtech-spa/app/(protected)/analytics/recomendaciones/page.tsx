"use client";

import { useEffect, useState } from "react";
import { obtenerRecomendaciones } from "@/lib/services/analytics";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas } from "@/lib/services/parcelas";
import { AlertaRecomendacion, Campo, Parcela } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeVerAlertas } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function RecomendacionesPage() {
  const { user } = useAuthContext();
  const [data, setData] = useState<AlertaRecomendacion[]>([]);
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
    obtenerRecomendaciones(campoSeleccionado, parcelaSeleccionada)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  if (!puedeVerAlertas(user)) {
    return <Card><p>No tenés permisos para ver alertas.</p></Card>;
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Alertas y Recomendaciones</h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Resultados combinados de alertas en tiempo real y recomendaciones batch
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
        <Card title="Resultados">
          <Table
            columns={[
              { header: "Tipo", accessor: (d: AlertaRecomendacion) => d.tipo === "ALERTA_TIEMPO_REAL" ? "⚡ Alerta" : "📋 Recomendación" },
              { header: "Fecha", accessor: (d: AlertaRecomendacion) => new Date(d.fechaEmision).toLocaleString() },
              { header: "Mensaje", accessor: (d: AlertaRecomendacion) => d.mensaje },
              { header: "Parcela", accessor: (d: AlertaRecomendacion) => d.nombreParcela },
            ]}
            data={data}
            keyExtractor={(d) => `${d.tipo}-${d.fechaEmision}`}
            emptyMessage="No hay resultados para esta parcela."
          />
        </Card>
      )}
    </div>
  );
}
