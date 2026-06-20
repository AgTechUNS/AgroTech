"use client";

import { useState } from "react";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: call reset-password API
    setSent(true);
  };

  if (sent) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          background: "#f1f5f9",
        }}
      >
        <div
          style={{
            background: "#fff",
            padding: "2rem",
            borderRadius: "8px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            width: "100%",
            maxWidth: 400,
            textAlign: "center",
          }}
        >
          <h2 style={{ margin: "0 0 0.5rem" }}>Revisá tu correo</h2>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>
            Si la cuenta existe, recibirás un enlace para restablecer tu contraseña.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "#f1f5f9",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: 360,
        }}
      >
        <h1 style={{ margin: "0 0 0.3rem", fontSize: "1.3rem" }}>
          Restablecer contraseña
        </h1>
        <p style={{ color: "#64748b", margin: "0 0 1.5rem", fontSize: "0.9rem" }}>
          Ingresá tu email y te enviaremos un enlace.
        </p>

        <div style={{ marginBottom: "1.5rem" }}>
          <label
            style={{
              display: "block",
              marginBottom: "0.3rem",
              fontSize: "0.85rem",
              fontWeight: 500,
            }}
          >
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              fontSize: "0.9rem",
              boxSizing: "border-box",
            }}
          />
        </div>

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "0.6rem",
            background: "#2c7be5",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            fontSize: "0.9rem",
            fontWeight: 500,
            cursor: "pointer",
          }}
        >
          Enviar enlace
        </button>

        <div style={{ marginTop: "1rem", textAlign: "center" }}>
          <a
            href="/login"
            style={{ color: "#2c7be5", fontSize: "0.85rem", textDecoration: "none" }}
          >
            Volver al inicio de sesión
          </a>
        </div>
      </form>
    </div>
  );
}
