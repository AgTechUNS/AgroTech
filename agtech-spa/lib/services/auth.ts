import { LoginResponse } from "@/lib/types";

export async function loginApi(emailUsuario: string, password: string): Promise<LoginResponse> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emailUsuario, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.code ?? "CREDENTIALS_INVALID");
  }
  return res.json();
}
