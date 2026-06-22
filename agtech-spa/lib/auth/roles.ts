import { JwtPayload, UserRole } from "@/lib/types";

export function puedeEditar(user: JwtPayload | null): boolean {
  return user?.role === "ADMIN";
}

export function puedeVerAlertas(user: JwtPayload | null): boolean {
  return user?.role === "ADMIN" || user?.role === "AGRONOMO";
}

export function puedeCrearReglas(user: JwtPayload | null): boolean {
  return user?.role === "ADMIN" || user?.role === "AGRONOMO";
}

export function roleLabel(role: UserRole): string {
  const labels: Record<UserRole, string> = {
    ADMIN: "Administrador",
    AGRONOMO: "Agrónomo",
  };
  return labels[role];
}
