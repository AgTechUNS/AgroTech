import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  const proxy = await proxyToBackend(request, "/external/weather", "GET");
  if (proxy) return proxy;
  return NextResponse.json(
    { error: { code: "UPSTREAM_ERROR", message: "Backend weather no disponible" } },
    { status: 502 }
  );
}
