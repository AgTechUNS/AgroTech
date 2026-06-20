import { NextRequest, NextResponse } from "next/server";
import { readCatalogo } from "@/lib/data/store";
import { getUserFromRequest } from "@/lib/auth/token";

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  return NextResponse.json(readCatalogo());
}
