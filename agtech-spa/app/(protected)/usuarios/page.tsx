"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { listarUsuarios, eliminarUsuario } from "@/lib/services/usuarios";
import { Usuario, UserRole } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar, roleLabel } from "@/lib/auth/roles";
import { Card, Table, Button, Spinner } from "@/components/ui";

export default function UsuariosPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!puedeEditar(user)) {
      router.push("/dashboard");
      return;
    }
    listarUsuarios()
      .then(setUsuarios)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, router]);

  const handleDelete = async (email: string) => {
    if (!confirm(`¿Eliminar a ${email}?`)) return;
    try {
      await eliminarUsuario(email);
      setUsuarios((prev) => prev.filter((a) => a.email !== email));
    } catch (e) {
      alert(e instanceof Error ? e.message : "Error al eliminar");
    }
  };

  if (!puedeEditar(user)) return null;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Usuarios</h1>
          <p style={{ color: "#64748b", margin: "0.3rem 0 0", fontSize: "0.9rem" }}>
            Gestioná los usuarios de la plataforma
          </p>
        </div>
        <Link href="/usuarios/crear">
          <Button>+ Nuevo usuario</Button>
        </Link>
      </div>

      <Card title="Listado">
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              { header: "Email", accessor: (a: Usuario) => a.email },
              { header: "Nombre", accessor: (a: Usuario) => a.nombre },
              {
                header: "Rol",
                accessor: (a: Usuario) => {
                  const colors: Record<UserRole, string> = { ADMIN: "#2c7be5", AGRONOMO: "#16a34a", PRODUCTOR: "#d97706" };
                  return <span style={{ color: colors[a.rol], fontWeight: 600 }}>{roleLabel(a.rol)}</span>;
                },
              },
              {
                header: "Acciones",
                accessor: (a: Usuario) =>
                  a.rol === "ADMIN" ? (
                    <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>—</span>
                  ) : (
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <Link href={`/usuarios/${encodeURIComponent(a.email)}/editar`}>
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
            data={usuarios}
            keyExtractor={(a) => a.email}
            emptyMessage="No hay usuarios registrados."
          />
        )}
      </Card>
    </div>
  );
}
