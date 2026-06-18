"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { listarCampos } from "@/lib/services/campos";
import { listarParcelas } from "@/lib/services/parcelas";
import { Campo, Parcela } from "@/lib/types";
import { Card, Table, Button, Spinner } from "@/components/ui";

const FieldsMap = dynamic(
  () => import("@/components/map/FieldsMap").then((m) => m.FieldsMap),
  { ssr: false }
);

export default function CampoDetallePage() {
  const params = useParams();
  const router = useRouter();
  const nombreCampo = decodeURIComponent(params.nombreCampo as string);
  const [campo, setCampo] = useState<Campo | null>(null);
  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listarCampos(1, 100).then((res) =>
        res.data.find((c) => c.nombreCampo === nombreCampo) ?? null
      ),
      listarParcelas(nombreCampo).then((res) => res.data),
    ])
      .then(([c, p]) => {
        setCampo(c);
        setParcelas(p);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [nombreCampo]);

  if (loading) return <Spinner />;

  if (!campo) {
    return (
      <Card>
        <p>Campo no encontrado.</p>
        <Button onClick={() => router.push("/campos")}>Volver</Button>
      </Card>
    );
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>{campo.nombreCampo}</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            {campo.descripcionCampo ?? "Sin descripción"}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link href={`/campos/${encodeURIComponent(nombreCampo)}/parcelas/crear`}>
            <Button>+ Nueva parcela</Button>
          </Link>
          <Button variant="ghost" onClick={() => router.push("/campos")}>
            Volver
          </Button>
        </div>
      </div>

      <Card style={{ padding: "0.5rem", marginBottom: "1.5rem" }}>
        <FieldsMap fields={[campo]} parcels={parcelas} height={400} />
      </Card>

      <Card title={`Parcelas (${parcelas.length})`}>
        <Table
          columns={[
            { header: "Parcela", accessor: (p: Parcela) => p.nombreParcela },
            { header: "Cultivo", accessor: (p: Parcela) => p.nombreCultivo ?? "—" },
            { header: "Descripción", accessor: (p: Parcela) => p.descripcionParcela ?? "—" },
          ]}
          data={parcelas}
          keyExtractor={(p) => p.nombreParcela}
          emptyMessage="Este campo no tiene parcelas aún."
        />
      </Card>
    </div>
  );
}
