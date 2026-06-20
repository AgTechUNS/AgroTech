"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { crearUsuario } from "@/lib/services/usuarios";
import { UserRole } from "@/lib/types";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { Card, Button } from "@/components/ui";

const ROLES: { value: UserRole; label: string }[] = [
  { value: "AGRONOMO", label: "Agrónomo" },
  { value: "PRODUCTOR", label: "Productor" },
];

export default function CrearUsuarioPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [email, setEmail] = useState("");
  const [rol, setRol] = useState<UserRole>("PRODUCTOR");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!puedeEditar(user)) router.push("/dashboard");
  }, [user, router]);

  if (!puedeEditar(user)) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) { setError("El email es obligatorio."); return; }
    setSubmitting(true);
    setError(null);
    try {
      await crearUsuario({ email: email.trim(), rol });
      router.push("/usuarios");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear usuario");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>Nuevo usuario</h1>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>Crear un nuevo usuario en la plataforma</p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem", maxWidth: 400 }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }} />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem" }}>Rol</label>
            <select value={rol} onChange={(e) => setRol(e.target.value as UserRole)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid var(--border)", borderRadius: "var(--radius)", fontSize: "0.9rem", background: "var(--bg-input)", color: "var(--text-primary)" }}>
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
          {error && <p style={{ color: "var(--danger)", fontSize: "0.85rem", margin: 0 }}>{error}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button type="submit" loading={submitting}>Guardar usuario</Button>
            <Button variant="ghost" onClick={() => router.push("/usuarios")}>Cancelar</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
