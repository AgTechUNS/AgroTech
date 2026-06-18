"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Button, Input, Card } from "@/components/ui";

const ERROR_LABELS: Record<string, string> = {
  CREDENTIALS_INVALID: "Email o contraseña incorrectos.",
  VALIDATION_ERROR: "Los datos ingresados no son válidos.",
  ACCOUNT_DISABLED: "La cuenta está deshabilitada.",
  ACCOUNT_NOT_FOUND: "No existe una cuenta con ese email.",
  TOO_MANY_ATTEMPTS: "Demasiados intentos. Intentá más tarde.",
};

function errorLabel(code: string): string {
  return ERROR_LABELS[code] ?? `Error: ${code}`;
}

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [emailUsuario, setEmailUsuario] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await login(emailUsuario, password);
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f1f5f9",
      }}
    >
      <Card style={{ width: "100%", maxWidth: 380 }}>
        <h1 style={{ margin: "0 0 1.5rem", fontSize: "1.4rem", textAlign: "center" }}>
          AgTech UNS
        </h1>

        {error && (
          <div
            role="alert"
            style={{
              color: "#c0392b",
              background: "#fdecea",
              border: "1px solid #f5c6cb",
              borderRadius: "6px",
              padding: "0.6rem 0.8rem",
              marginBottom: "1rem",
              fontSize: "0.9rem",
            }}
          >
            {errorLabel(error)}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Input
            label="Email"
            type="email"
            value={emailUsuario}
            onChange={(e) => setEmailUsuario(e.target.value)}
            required
            autoComplete="email"
            placeholder="usuario@agtech.uns.edu.ar"
          />

          <Input
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder="••••••••"
          />

          <Button type="submit" loading={isLoading}>
            Ingresar
          </Button>
        </form>

        <Link
          href="/reset-password"
          style={{
            display: "block",
            textAlign: "center",
            fontSize: "0.85rem",
            color: "#2c7be5",
            textDecoration: "none",
            marginTop: "1rem",
          }}
        >
          ¿Olvidaste tu contraseña?
        </Link>
      </Card>
    </main>
  );
}
