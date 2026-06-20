import { NextRequest, NextResponse } from "next/server";
import { getUserFromRequest } from "@/lib/auth/token";
import { WeatherResponse } from "@/lib/types";

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const lat = parseFloat(searchParams.get("lat") ?? "");
  const lon = parseFloat(searchParams.get("lon") ?? "");

  if (isNaN(lat) || isNaN(lon)) {
    return NextResponse.json(
      { error: { code: "VALIDATION_ERROR", message: "lat y lon son requeridos" } },
      { status: 400 }
    );
  }

  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    return NextResponse.json(
      { error: { code: "VALIDATION_ERROR", message: "lat (-90 a 90) y lon (-180 a 180)" } },
      { status: 400 }
    );
  }

  const data: WeatherResponse = {
    temperature_celsius: Math.round((15 + Math.random() * 15) * 10) / 10,
    humidity_percent: Math.round((40 + Math.random() * 40) * 10) / 10,
    timestamp: new Date().toISOString(),
    latitude: lat,
    longitude: lon,
  };

  return NextResponse.json(data);
}
