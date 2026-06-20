"use client";

import { ReactNode } from "react";

interface Column<T> {
  header: string;
  accessor: (item: T) => ReactNode;
  align?: "left" | "center" | "right";
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
}

export function Table<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = "No hay datos disponibles.",
}: TableProps<T>) {
  if (data.length === 0) {
    return (
      <p style={{ textAlign: "center", color: "#888", padding: "2rem" }}>
        {emptyMessage}
      </p>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #e9ecef" }}>
            {columns.map((col) => (
              <th
                key={col.header}
                style={{
                  textAlign: col.align ?? "left",
                  padding: "0.6rem 0.8rem",
                  fontWeight: 600,
                  color: "#495057",
                  whiteSpace: "nowrap",
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr
              key={keyExtractor(item)}
              style={{
                borderBottom: "1px solid #e9ecef",
                background: i % 2 === 0 ? "#fff" : "#f8f9fa",
              }}
            >
              {columns.map((col) => (
                <td
                  key={col.header}
                  style={{
                    textAlign: col.align ?? "left",
                    padding: "0.6rem 0.8rem",
                  }}
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
