"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { listarUsuarios, editarUsuario } from "@/lib/services/usuarios";
import { UserRole } from "@/lib/types";
import { Card, Button, Spinner } from "@/components/ui";

const ROLES: { value: UserRole; label: string }[] = [
  { value: "ADMIN", label: "Administrador" },
  { value: "AGRONOMO", label: "Agrónomo" },
];

export default function EditarUsuarioPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const email = decodeURIComponent(params.email as string);
  const [nombre, setNombre] = useState("");
  const [rol, setRol] = useState<UserRole>("AGRONOMO");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!puedeEditar(user)) {
      router.push("/dashboard");
      return;
    }
    listarUsuarios()
      .then((list) => {
        const a = list.find((x) => x.email === email);
        if (!a) { router.push("/usuarios"); return; }
        setNombre(a.nombre);
        setRol(a.rol);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, email, router]);

  if (!puedeEditar(user)) return null;
  if (loading) return <Spinner />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!nombre) { setError("El nombre es obligatorio"); return; }
    setSaving(true);
    try {
      await editarUsuario(email, { nombre, password: password || undefined, rol });
      router.push("/usuarios");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al editar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Editar usuario</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1rem", fontSize: "0.9rem" }}>{email}</p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 400 }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "var(--text-primary)" }}>Nombre</label>
            <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }} />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "var(--text-primary)" }}>Rol</label>
            <select value={rol} onChange={(e) => setRol(e.target.value as UserRole)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }}>
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "var(--text-primary)" }}>
              Nueva contraseña <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>(dejar vacío para mantener)</span>
            </label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }}
              placeholder="Nueva contraseña" />
          </div>
          {error && <p style={{ color: "var(--danger)", fontSize: "0.85rem", margin: 0 }}>{error}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button type="submit" disabled={saving}>{saving ? "Guardando..." : "Guardar cambios"}</Button>
            <Button variant="ghost" onClick={() => router.push("/usuarios")}>Cancelar</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
