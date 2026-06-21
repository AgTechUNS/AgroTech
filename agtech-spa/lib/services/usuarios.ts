import { Usuario } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarUsuarios(): Promise<Usuario[]> {
  const res = await fetchWithAuth("/api/usuarios");
  if (!res.ok) throw new Error("Error al obtener usuarios");
  const json = await res.json();
  if (Array.isArray(json)) return json as Usuario[];
  return json.data as Usuario[];
}

export async function crearUsuario(payload: { email: string; rol: "ADMIN" | "AGRONOMO" | "PRODUCTOR" }): Promise<void> {
  const res = await fetchWithAuth("/api/usuarios", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear usuario");
  }
}

export async function editarUsuario(email: string, payload: { nombre?: string; password?: string; rol?: "ADMIN" | "AGRONOMO" | "PRODUCTOR" }): Promise<void> {
  const res = await fetchWithAuth(`/api/usuarios/${encodeURIComponent(email)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al editar usuario");
  }
}

export async function eliminarUsuario(email: string): Promise<void> {
  const res = await fetchWithAuth(`/api/usuarios/${encodeURIComponent(email)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al eliminar usuario");
  }
}
