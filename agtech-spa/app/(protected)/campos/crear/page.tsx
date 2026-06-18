"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { crearCampo } from "@/lib/services/campos";
import { Card, Button, Input } from "@/components/ui";

const MapSelector = dynamic(
  () => import("@/components/map/MapSelector").then((m) => m.MapSelector),
  { ssr: false }
);

const schema = z.object({
  nombreCampo: z.string().min(1, "El nombre es obligatorio"),
  descripcionCampo: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function CrearCampoPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [polygon, setPolygon] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  async function onSubmit(data: FormData) {
    if (!polygon) {
      setError("Dibujá el perímetro del campo en el mapa.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await crearCampo({
        nombreCampo: data.nombreCampo,
        descripcionCampo: data.descripcionCampo || undefined,
        coordenadasCampo: polygon,
      });
      router.push("/campos");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el campo.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        Nuevo campo
      </h1>
      <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
        Registrá una nueva unidad productiva
      </p>

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
          <Input
            label="Nombre del campo"
            placeholder="Ej: Campo Los Pinos"
            error={errors.nombreCampo?.message}
            {...register("nombreCampo")}
          />

          <Input
            label="Descripción (opcional)"
            placeholder="Ej: Establecimiento norte destinado a cultivos rotativos"
            error={errors.descripcionCampo?.message}
            {...register("descripcionCampo")}
          />

          <div>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>
              Perímetro del campo
            </span>
            <MapSelector onPolygonChange={setPolygon} />
            {polygon && (
              <span style={{ fontSize: "0.8rem", color: "#27ae60", marginTop: "0.3rem", display: "block" }}>
                ✅ Polígono definido
              </span>
            )}
          </div>

          {error && (
            <div style={{ color: "#e74c3c", fontSize: "0.9rem", background: "#fdecea", padding: "0.6rem", borderRadius: "6px" }}>
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.8rem" }}>
            <Button type="submit" loading={submitting}>
              Guardar campo
            </Button>
            <Button variant="ghost" onClick={() => router.push("/campos")}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
