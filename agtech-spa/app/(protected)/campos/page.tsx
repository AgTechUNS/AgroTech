"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { listarCampos } from "@/lib/services/campos";
import { Campo } from "@/lib/types";
import { Card, Table, Button, Spinner } from "@/components/ui";

const FieldsMap = dynamic(
  () => import("@/components/map/FieldsMap").then((m) => m.FieldsMap),
  { ssr: false }
);

export default function CamposListPage() {
  const [campos, setCampos] = useState<Campo[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    setLoading(true);
    listarCampos(page)
      .then((res) => {
        setCampos(res.data);
        setTotalPages(res.pagination.totalPages);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Campos</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Unidades productivas registradas
          </p>
        </div>
        <Link href="/campos/crear">
          <Button>+ Nuevo campo</Button>
        </Link>
      </div>

      <Card style={{ marginBottom: "1.5rem", padding: "0.5rem" }}>
        {campos.length > 0 && <FieldsMap fields={campos} height={350} />}
      </Card>

      <Card title="Listado">
        {loading ? (
          <Spinner />
        ) : (
          <>
            <Table
              columns={[
                { header: "Nombre", accessor: (c: Campo) => (
                  <Link href={`/campos/${encodeURIComponent(c.nombreCampo)}`} style={{ color: "#2c7be5", textDecoration: "none" }}>
                    {c.nombreCampo}
                  </Link>
                )},
                { header: "Descripción", accessor: (c: Campo) => c.descripcionCampo ?? "—" },
                { header: "Coordenadas", accessor: () => "GeoJSON" },
              ]}
              data={campos}
              keyExtractor={(c) => c.nombreCampo}
              emptyMessage="No hay campos registrados. Creá el primero."
            />
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", marginTop: "1rem" }}>
                <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  Anterior
                </Button>
                <span style={{ padding: "0.5rem", color: "#64748b", fontSize: "0.9rem" }}>
                  {page} / {totalPages}
                </span>
                <Button variant="ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                  Siguiente
                </Button>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
}
