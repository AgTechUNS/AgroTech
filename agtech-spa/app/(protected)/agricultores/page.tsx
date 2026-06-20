"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { listarAgricultores, eliminarAgricultor } from "@/lib/services/agricultores";
import { Agricultor } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function AgricultoresPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [agricultores, setAgricultores] = useState<Agricultor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!puedeEditar(user)) {
      router.push("/dashboard");
      return;
    }
    listarAgricultores()
      .then(setAgricultores)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, router]);

  const handleDelete = async (email: string) => {
    if (!confirm(`¿Eliminar a ${email}?`)) return;
    try {
      await eliminarAgricultor(email);
      setAgricultores((prev) => prev.filter((a) => a.email !== email));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error al eliminar");
    }
  };

  if (!puedeEditar(user)) return null;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Agricultores</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Gestioná los usuarios de la plataforma
          </p>
        </div>
        <Link href="/agricultores/crear">
          <Button>+ Nuevo agricultor</Button>
        </Link>
      </div>

      <Card title="Listado">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Email", accessor: (a: Agricultor) => a.email },
              { header: "Nombre", accessor: (a: Agricultor) => a.nombre },
              {
                header: "Rol",
                accessor: (a: Agricultor) =>
                  a.rol === "ADMIN"
                    ? <span style={{ color: "#2c7be5", fontWeight: 600 }}>Administrador</span>
                    : <span style={{ color: "#64748b" }}>Agricultor</span>,
              },
              {
                header: "Acciones",
                accessor: (a: Agricultor) =>
                  a.rol === "ADMIN" ? (
                    <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>—</span>
                  ) : (
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <Link href={`/agricultores/${encodeURIComponent(a.email)}/editar`}>
                        <Button variant="ghost" style={{ fontSize: "0.8rem", padding: "0.3rem 0.6rem" }}>Editar</Button>
                      </Link>
                      <Button
                        variant="ghost"
                        style={{ fontSize: "0.8rem", padding: "0.3rem 0.6rem", color: "#dc2626" }}
                        onClick={() => handleDelete(a.email)}
                      >
                        Eliminar
                      </Button>
                    </div>
                  ),
              },
            ]}
            data={agricultores}
            keyExtractor={(a) => a.email}
            emptyMessage="No hay agricultores registrados."
          />
        )}
      </Card>
    </div>
  );
}
