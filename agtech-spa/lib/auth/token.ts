import { NextRequest } from "next/server";
import { JwtPayload } from "@/lib/types";

function b64UrlDecode(str: string): string {
  return Buffer.from(str.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString();
}

export function getUserFromRequest(request: NextRequest): JwtPayload | null {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return null;
  const token = authHeader.slice(7);
  try {
    const payload = b64UrlDecode(token.split(".")[1]);
    return JSON.parse(payload) as JwtPayload;
  } catch {
    return null;
  }
}

export function getAdminEmail(user: JwtPayload): string {
  return user.adminEmail ?? user.email;
}

export function requireAdmin(request: NextRequest): JwtPayload | null {
  const user = getUserFromRequest(request);
  if (!user || user.role !== "ADMIN") return null;
  return user;
}
