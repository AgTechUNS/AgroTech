"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/contexts/AuthContext";
import { puedeEditar } from "@/lib/auth/roles";
import { crearAgricultor } from "@/lib/services/agricultores";
import { Card, Button } from "@/components/ui";

export default function CrearAgricultorPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const [email, setEmail] = useState("");
  const [nombre, setNombre] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  if (!puedeEditar(user)) {
    router.push("/dashboard");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email || !nombre || !password) {
      setError("Todos los campos son obligatorios");
      return;
    }
    setSaving(true);
    try {
      await crearAgricultor({ email, nombre, password });
      router.push("/agricultores");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Nuevo agricultor</h1>

      <Card>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 400 }}>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "#374151" }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #d1d5db", borderRadius: "6px", fontSize: "0.9rem" }}
              placeholder="agricultor@email.com"
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "#374151" }}>
              Nombre
            </label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #d1d5db", borderRadius: "6px", fontSize: "0.9rem" }}
              placeholder="Nombre del agricultor"
            />
          </div>
          <div>
            <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.3rem", color: "#374151" }}>
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", border: "1px solid #d1d5db", borderRadius: "6px", fontSize: "0.9rem" }}
              placeholder="Contraseña"
            />
          </div>
          {error && <p style={{ color: "#dc2626", fontSize: "0.85rem", margin: 0 }}>{error}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear agricultor"}</Button>
            <Button variant="ghost" onClick={() => router.push("/agricultores")}>Cancelar</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
