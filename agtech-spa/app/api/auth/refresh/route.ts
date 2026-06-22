import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function POST(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/auth/refresh", "POST");
  return proxy ?? NextResponse.json(
    { error: { code: "SERVICE_UNAVAILABLE", message: "Backend no disponible" } },
    { status: 502 }
  );
}
