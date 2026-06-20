"use client";

import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, style, ...rest }, ref) => {
    return (
      <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{label}</span>
        <input
          ref={ref}
          style={{
            padding: "0.5rem 0.75rem",
            borderRadius: "6px",
            border: error ? "1px solid #e74c3c" : "1px solid #ccc",
            fontSize: "1rem",
            outline: "none",
            transition: "border-color 0.15s",
            ...style,
          }}
          {...rest}
        />
        {error && (
          <span style={{ fontSize: "0.78rem", color: "#e74c3c" }}>
            {error}
          </span>
        )}
      </label>
    );
  }
);

Input.displayName = "Input";
