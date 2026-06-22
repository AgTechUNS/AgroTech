import { NextRequest, NextResponse } from "next/server";
import { proxyToBackend } from "@/lib/proxy";

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  const backendPath = `/external/satelital/${params.path.join("/")}`;
  const proxy = await proxyToBackend(request, backendPath, "GET");
  if (proxy) return proxy;
  return NextResponse.json(
    { error: { code: "UPSTREAM_ERROR", message: "Backend satelital no disponible" } },
    { status: 502 }
  );
}
