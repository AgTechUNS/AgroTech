"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, AgTechError } from "@/lib/api";

const ERROR_LABELS: Record<string, string> = {
  RESET_TOKEN_INVALID:
    "El token es inválido o ha expirado. Solicitá un nuevo enlace de recuperación.",
  PASSWORDS_MISMATCH: "Las contraseñas no coinciden.",
  VALIDATION_ERROR: "Los datos ingresados no son válidos.",
  UNKNOWN_ERROR: "Ocurrió un error inesperado. Intentá de nuevo.",
};

function errorLabel(code: string): string {
  return ERROR_LABELS[code] ?? `Error: ${code}`;
}

export default function ResetPasswordConfirmPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    if (!success) return;
    if (countdown === 0) {
      router.push("/login");
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [success, countdown, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (nuevaPassword !== confirmarPassword) {
      setError("PASSWORDS_MISMATCH");
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/auth/reset-confirm", {
        token,
        nuevaPassword,
        confirmarPassword,
      });
      setSuccess(true);
    } catch (err) {
      if (err instanceof AgTechError) {
        setError(err.apiError.code);
      } else {
        setError("UNKNOWN_ERROR");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f5f5",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "360px",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.4rem", textAlign: "center" }}>
          Nueva contraseña
        </h1>

        {success ? (
          <p
            role="status"
            style={{
              color: "#27ae60",
              background: "#eafaf1",
              border: "1px solid #a9dfbf",
              borderRadius: "4px",
              padding: "0.6rem 0.8rem",
              margin: 0,
              fontSize: "0.9rem",
              textAlign: "center",
            }}
          >
            ¡Contraseña actualizada! Redirigiendo en {countdown}…
          </p>
        ) : (
          <>
            {error && (
              <p
                role="alert"
                style={{
                  color: "#c0392b",
                  background: "#fdecea",
                  border: "1px solid #f5c6cb",
                  borderRadius: "4px",
                  padding: "0.6rem 0.8rem",
                  margin: 0,
                  fontSize: "0.9rem",
                }}
              >
                {errorLabel(error)}
              </p>
            )}

            <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Token</span>
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                autoComplete="off"
                placeholder="Pegá el token recibido por email"
                style={{
                  padding: "0.5rem 0.75rem",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                  fontSize: "1rem",
                }}
              />
            </label>

            <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>
                Nueva contraseña
              </span>
              <input
                type="password"
                value={nuevaPassword}
                onChange={(e) => setNuevaPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
                placeholder="Mínimo 8 caracteres"
                style={{
                  padding: "0.5rem 0.75rem",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                  fontSize: "1rem",
                }}
              />
            </label>

            <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>
                Confirmar contraseña
              </span>
              <input
                type="password"
                value={confirmarPassword}
                onChange={(e) => setConfirmarPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
                placeholder="Repetí la nueva contraseña"
                style={{
                  padding: "0.5rem 0.75rem",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                  fontSize: "1rem",
                }}
              />
            </label>

            <button
              type="submit"
              disabled={isLoading}
              style={{
                padding: "0.6rem",
                borderRadius: "4px",
                border: "none",
                background: isLoading ? "#aaa" : "#2c7be5",
                color: "#fff",
                fontSize: "1rem",
                cursor: isLoading ? "not-allowed" : "pointer",
                fontWeight: 600,
              }}
            >
              {isLoading ? "Guardando…" : "Guardar contraseña"}
            </button>
          </>
        )}

        <Link
          href="/login"
          style={{
            textAlign: "center",
            fontSize: "0.85rem",
            color: "#2c7be5",
            textDecoration: "none",
          }}
        >
          ← Volver al inicio de sesión
        </Link>
      </form>
    </main>
  );
}
