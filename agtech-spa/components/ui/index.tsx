"use client";

import React from "react";

interface CardProps {
  title?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  onClick?: () => void;
  hover?: boolean;
}

export function Card({ title, children, style, onClick, hover }: CardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        background: "var(--bg-glass)",
        backdropFilter: "var(--blur)",
        WebkitBackdropFilter: "var(--blur)",
        borderRadius: "var(--radius)",
        border: "1px solid var(--border)",
        padding: "1.25rem",
        boxShadow: "var(--shadow-sm)",
        transition: "all var(--transition)",
        cursor: onClick ? "pointer" : undefined,
        ...(hover
          ? { ":hover": { background: "var(--bg-glass-hover)", borderColor: "var(--border-hover)", boxShadow: "var(--shadow)" } }
          : {}),
        ...style,
      }}
      onMouseEnter={(e) => {
        if (hover) {
          e.currentTarget.style.background = "var(--bg-glass-hover)";
          e.currentTarget.style.borderColor = "var(--border-hover)";
          e.currentTarget.style.boxShadow = "var(--shadow)";
        }
      }}
      onMouseLeave={(e) => {
        if (hover) {
          e.currentTarget.style.background = "var(--bg-glass)";
          e.currentTarget.style.borderColor = "var(--border)";
          e.currentTarget.style.boxShadow = "var(--shadow-sm)";
        }
      }}
    >
      {title && (
        <h3 style={{ margin: "0 0 0.75rem", fontSize: "1rem", fontWeight: 600, color: "var(--text-primary)" }}>
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}

interface TableProps<T> {
  columns: { header: string; accessor: (item: T) => React.ReactNode }[];
  data: T[];
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
}

export function Table<T>({ columns, data, keyExtractor, emptyMessage }: TableProps<T>) {
  if (data.length === 0) {
    return (
      <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "2rem" }}>
        {emptyMessage ?? "Sin datos"}
      </p>
    );
  }

  return (
    <div style={{ overflowX: "auto", borderRadius: "var(--radius)", border: "1px solid var(--border)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--bg-glass)" }}>
            {columns.map((col) => (
              <th
                key={col.header}
                style={{
                  textAlign: "left",
                  padding: "0.75rem 1rem",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  color: "var(--text-muted)",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              style={{ borderBottom: "1px solid var(--border)", transition: "background var(--transition)" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-glass-hover)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "")}
            >
              {columns.map((col) => (
                <td
                  key={col.header}
                  style={{ padding: "0.75rem 1rem", fontSize: "0.9rem", color: "var(--text-primary)" }}
                >
                  {col.accessor(item)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "danger";
  loading?: boolean;
}

export function Button({ variant = "primary", loading, disabled, style, ...rest }: ButtonProps) {
  const isDisabled = disabled || loading;
  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      background: "var(--accent)",
      color: "#fff",
      border: "none",
    },
    ghost: {
      background: "var(--bg-glass)",
      color: "var(--text-primary)",
      border: "1px solid var(--border)",
    },
    danger: {
      background: "var(--danger-bg)",
      color: "var(--danger)",
      border: "1px solid transparent",
    },
  };

  const base = variantStyles[variant];

  return (
    <button
      disabled={isDisabled}
      style={{
        ...base,
        padding: "0.5rem 1rem",
        borderRadius: "var(--radius)",
        cursor: isDisabled ? "not-allowed" : "pointer",
        fontSize: "0.9rem",
        fontWeight: 500,
        fontFamily: "inherit",
        opacity: isDisabled ? 0.5 : 1,
        backdropFilter: variant === "ghost" ? "var(--blur)" : undefined,
        WebkitBackdropFilter: variant === "ghost" ? "var(--blur)" : undefined,
        transition: "all var(--transition)",
        boxShadow: variant === "primary" ? "var(--shadow-sm)" : undefined,
        ...style,
      }}
      onMouseEnter={(e) => {
        if (!isDisabled) {
          if (variant === "primary") {
            e.currentTarget.style.background = "var(--accent-hover)";
            e.currentTarget.style.boxShadow = "var(--shadow)";
          } else if (variant === "ghost") {
            e.currentTarget.style.background = "var(--bg-glass-hover)";
            e.currentTarget.style.borderColor = "var(--border-hover)";
          }
        }
      }}
      onMouseLeave={(e) => {
        if (!isDisabled) {
          if (variant === "primary") {
            e.currentTarget.style.background = "var(--accent)";
            e.currentTarget.style.boxShadow = "var(--shadow-sm)";
          } else if (variant === "ghost") {
            e.currentTarget.style.background = "var(--bg-glass)";
            e.currentTarget.style.borderColor = "var(--border)";
          }
        }
      }}
      {...rest}
    />
  );
}

interface InputProps {
  label?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  step?: string;
  required?: boolean;
  disabled?: boolean;
  name?: string;
  min?: string | number;
  max?: string | number;
  error?: string;
  style?: React.CSSProperties;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input({ label, error, style, ...rest }, ref) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
      {label && (
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
          {label}
        </span>
      )}
      <input
        ref={ref}
        {...rest}
        style={{
          padding: "0.5rem 0.75rem",
          borderRadius: "var(--radius)",
          border: error ? "1px solid var(--danger)" : "1px solid var(--border)",
          fontSize: "0.95rem",
          fontFamily: "inherit",
          background: "var(--bg-input)",
          color: "var(--text-primary)",
          outline: "none",
          transition: "border-color var(--transition), box-shadow var(--transition)",
          boxShadow: error ? "0 0 0 3px var(--danger-bg)" : "none",
          ...style,
        }}
        onFocus={(e) => {
          if (!error) {
            e.currentTarget.style.borderColor = "var(--accent)";
            e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-bg)";
          }
        }}
        onBlur={(e) => {
          if (!error) {
            e.currentTarget.style.borderColor = "var(--border)";
            e.currentTarget.style.boxShadow = "none";
          }
          rest.onBlur?.(e);
        }}
      />
      {error && <span style={{ fontSize: "0.8rem", color: "var(--danger)" }}>{error}</span>}
    </label>
  );
});

export function Spinner() {
  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
      <div
        style={{
          width: 24,
          height: 24,
          border: "2px solid var(--border)",
          borderTopColor: "var(--accent)",
          borderRadius: "50%",
          animation: "spin 0.6s linear infinite",
        }}
      />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
