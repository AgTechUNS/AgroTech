import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL;

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  if (!BACKEND_URL) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: `Ruta /api/${params.path.join("/")} no encontrada en modo mock` } }, { status: 404 });
  }
  return proxyRequest(request, params.path, "GET");
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  if (!BACKEND_URL) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: `Ruta /api/${params.path.join("/")} no encontrada en modo mock` } }, { status: 404 });
  }
  return proxyRequest(request, params.path, "POST");
}

export async function PUT(request: NextRequest, { params }: { params: { path: string[] } }) {
  if (!BACKEND_URL) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: `Ruta /api/${params.path.join("/")} no encontrada en modo mock` } }, { status: 404 });
  }
  return proxyRequest(request, params.path, "PUT");
}

export async function DELETE(request: NextRequest, { params }: { params: { path: string[] } }) {
  if (!BACKEND_URL) {
    return NextResponse.json({ error: { code: "NOT_FOUND", message: `Ruta /api/${params.path.join("/")} no encontrada en modo mock` } }, { status: 404 });
  }
  return proxyRequest(request, params.path, "DELETE");
}

async function proxyRequest(request: NextRequest, path: string[], method: string): Promise<NextResponse> {
  const targetUrl = new URL(`${BACKEND_URL}/${path.join("/")}`);
  targetUrl.search = new URL(request.url).search;

  const headers: Record<string, string> = {};
  const authHeader = request.headers.get("Authorization");
  if (authHeader) headers["Authorization"] = authHeader;
  headers["Content-Type"] = "application/json";

  let body: BodyInit | undefined;
  if (method !== "GET" && method !== "HEAD") {
    body = await request.text();
  }

  try {
    const res = await fetch(targetUrl.toString(), { method, headers, body });
    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return NextResponse.json(
      { error: { code: "PROXY_ERROR", message: `Error al conectar con backend en ${BACKEND_URL}` } },
      { status: 502 }
    );
  }
}
