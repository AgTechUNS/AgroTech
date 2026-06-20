"use client";

import React from "react";

interface CardProps {
  title?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

export function Card({ title, children, style }: CardProps) {
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "8px",
        border: "1px solid #e2e8f0",
        padding: "1rem",
        ...style,
      }}
    >
      {title && (
        <h3 style={{ margin: "0 0 1rem", fontSize: "1rem", fontWeight: 600 }}>
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

export function Table<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage,
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <p style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>
        {emptyMessage ?? "Sin datos"}
      </p>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #e2e8f0" }}>
            {columns.map((col) => (
              <th
                key={col.header}
                style={{
                  textAlign: "left",
                  padding: "0.75rem 0.5rem",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  color: "#64748b",
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
              style={{ borderBottom: "1px solid #f1f5f9" }}
            >
              {columns.map((col) => (
                <td
                  key={col.header}
                  style={{ padding: "0.75rem 0.5rem", fontSize: "0.9rem" }}
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
  variant?: "primary" | "ghost";
  loading?: boolean;
}

export function Button({
  variant = "primary",
  loading,
  disabled,
  style,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading;
  const baseStyle: React.CSSProperties =
    variant === "ghost"
      ? {
          background: "transparent",
          border: "none",
          color: "#2c7be5",
          cursor: "pointer",
          fontSize: "0.9rem",
          padding: "0.4rem 0.8rem",
          borderRadius: "6px",
        }
      : {
          background: "#2c7be5",
          color: "#fff",
          border: "none",
          padding: "0.5rem 1rem",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "0.9rem",
          fontWeight: 500,
        };

  return <button disabled={isDisabled} style={{ ...baseStyle, opacity: isDisabled ? 0.6 : 1, ...style }} {...rest} />;
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

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  function Input({ label, error, style, ...rest }, ref) {
    return (
      <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        {label && <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{label}</span>}
        <input
          ref={ref}
          {...rest}
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "6px",
            border: error ? "1px solid #e74c3c" : "1px solid #ccc",
            fontSize: "1rem",
            background: "#fff",
            outline: "none",
            ...style,
          }}
        />
        {error && <span style={{ fontSize: "0.8rem", color: "#e74c3c" }}>{error}</span>}
      </label>
    );
  }
);

export function Spinner() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        padding: "2rem",
      }}
    >
      <div
        style={{
          width: 24,
          height: 24,
          border: "3px solid #e2e8f0",
          borderTopColor: "#2c7be5",
          borderRadius: "50%",
          animation: "spin 0.6s linear infinite",
        }}
      />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
