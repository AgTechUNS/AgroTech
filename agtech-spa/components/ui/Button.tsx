"use client";

import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  loading?: boolean;
}

const VARIANTS: Record<string, React.CSSProperties> = {
  primary: { background: "#2c7be5", color: "#fff" },
  secondary: { background: "#6c757d", color: "#fff" },
  danger: { background: "#e74c3c", color: "#fff" },
  ghost: { background: "transparent", color: "#2c7be5", border: "1px solid #2c7be5" },
};

export function Button({
  variant = "primary",
  loading,
  disabled,
  children,
  style,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading;
  return (
    <button
      disabled={isDisabled}
      style={{
        padding: "0.6rem 1.2rem",
        borderRadius: "6px",
        border: "none",
        fontSize: "0.95rem",
        fontWeight: 600,
        cursor: isDisabled ? "not-allowed" : "pointer",
        opacity: isDisabled ? 0.6 : 1,
        transition: "opacity 0.15s",
        ...VARIANTS[variant],
        ...style,
      }}
      {...rest}
    >
      {loading ? "Cargando…" : children}
    </button>
  );
}
