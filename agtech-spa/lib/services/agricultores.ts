import { Agricultor } from "@/lib/types";
import { fetchWithAuth } from "@/lib/auth";

export async function listarAgricultores(): Promise<Agricultor[]> {
  const res = await fetchWithAuth("/api/agricultores");
  if (!res.ok) throw new Error("Error al obtener agricultores");
  const json = await res.json();
  return json.data as Agricultor[];
}

export async function crearAgricultor(payload: { email: string; nombre: string; password: string }): Promise<void> {
  const res = await fetchWithAuth("/api/agricultores", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al crear agricultor");
  }
}

export async function editarAgricultor(email: string, payload: { nombre?: string; password?: string }): Promise<void> {
  const res = await fetchWithAuth(`/api/agricultores/${encodeURIComponent(email)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al editar agricultor");
  }
}

export async function eliminarAgricultor(email: string): Promise<void> {
  const res = await fetchWithAuth(`/api/agricultores/${encodeURIComponent(email)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? "Error al eliminar agricultor");
  }
}
