"use client";

import { ReactNode } from "react";

interface CardProps {
  title?: string;
  children: ReactNode;
  style?: React.CSSProperties;
}

export function Card({ title, children, style }: CardProps) {
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
        padding: "1.5rem",
        ...style,
      }}
    >
      {title && (
        <h2 style={{ margin: "0 0 1rem", fontSize: "1.15rem", fontWeight: 600 }}>
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}
