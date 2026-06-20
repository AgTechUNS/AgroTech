import { JwtPayload } from "@/lib/types";

export function puedeEditar(user: JwtPayload | null): boolean {
  return user?.role === "ADMIN";
}
