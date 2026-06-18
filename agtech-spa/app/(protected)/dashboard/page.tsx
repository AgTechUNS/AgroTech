"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { jwtDecode } from "jwt-decode";
import { getAccessToken } from "@/lib/auth";
import { useAuthContext } from "@/contexts/AuthContext";
import { Card, Table, Button } from "@/components/ui";

interface Claim {
  key: string;
  value: string;
}

const SKIP_CLAIMS = new Set(["iat", "exp", "nbf", "jti", "iss", "aud", "sub"]);

function getRemainingSeconds(exp: number): number {
  return Math.max(0, exp - Math.floor(Date.now() / 1000));
}

export default function DashboardPage() {
  const router = useRouter();
  const { logout } = useAuthContext();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [remaining, setRemaining] = useState(0);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    try {
      const payload = jwtDecode<Record<string, unknown>>(token);
      const items: Claim[] = Object.entries(payload)
        .filter(([k]) => !SKIP_CLAIMS.has(k))
        .map(([key, value]) => ({ key, value: String(value) }));
      setClaims(items);

      const exp = payload.exp;
      if (typeof exp === "number") {
        setRemaining(getRemainingSeconds(exp));
        const interval = setInterval(() => {
          setRemaining(getRemainingSeconds(exp));
        }, 1000);
        return () => clearInterval(interval);
      }
    } catch {
      router.replace("/login");
    }
  }, [router]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${String(sec).padStart(2, "0")}`;
  };

  const expColor = remaining > 300 ? "#27ae60" : remaining > 60 ? "#f39c12" : "#e74c3c";

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Dashboard
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Resumen de la sesión actual
      </p>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        <Card style={{ flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: "0.3rem" }}>
            Sesión expira en
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, color: expColor }}>
            {formatTime(remaining)}
          </div>
        </Card>
        <Card style={{ flex: 1, minWidth: 200 }}>
          <Button variant="danger" onClick={logout}>
            Cerrar sesión
          </Button>
        </Card>
      </div>

      <Card title="Claims del JWT">
        <Table
          columns={[
            { header: "Claim", accessor: (c: Claim) => c.key },
            { header: "Valor", accessor: (c: Claim) => c.value },
          ]}
          data={claims}
          keyExtractor={(c) => c.key}
          emptyMessage="No hay claims para mostrar."
        />
      </Card>
    </div>
  );
}
