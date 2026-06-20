"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { listarAgricultores, editarAgricultor } from "@/lib/services/agricultores";
import { Card, Button, Spinner } from "@/components/ui";

export default function EditarAgricultorPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthContext();
  const email = decodeURIComponent(params.email as string);
  const [nombre, setNombre] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!puedeEditar(user)) {
      router.push("/dashboard");
      return;
    }
    listarAgricultores()
      .then((list) => {
        const a = list.find((x) => x.email === email);
        if (!a) {
          router.push("/agricultores");
          return;
        }
        setNombre(a.nombre);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, email, router]);

  if (!puedeEditar(user)) return null;
  if (loading) return <Spinner />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!nombre) {
      setError("El nombre es obligatorio");
      return;
    }
    setSaving(true);
    try {
      await editarAgricultor(email, { nombre, password: password || undefined });
      router.push("/agricultores");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al editar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Editar agricultor</h1>
      <p style={{ color: "#64748b", marginBottom: "1rem", fontSize: "0.9rem" }}>{email}</p>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 400 }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "#374151" }}>
              Nombre
            </label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #d1d5db", borderRadius: "6px", fontSize: "0.9rem" }}
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "#374151" }}>
              Nueva contraseña <span style={{ fontWeight: 400, color: "#94a3b8" }}>(dejar vacío para mantener)</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #d1d5db", borderRadius: "6px", fontSize: "0.9rem" }}
              placeholder="Nueva contraseña"
            />
          </div>
          {error && <p style={{ color: "#dc2626", fontSize: "0.85rem", margin: 0 }}>{error}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button type="submit" disabled={saving}>{saving ? "Guardando..." : "Guardar cambios"}</Button>
            <Button variant="ghost" onClick={() => router.push("/agricultores")}>Cancelar</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
