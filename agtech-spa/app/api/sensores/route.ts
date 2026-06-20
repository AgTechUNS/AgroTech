import { NextRequest, NextResponse } from "next/server";
import { readSensores } from "@/lib/data/store";
import { getUserFromRequest, getAdminEmail } from "@/lib/auth/token";

export async function GET(request: NextRequest) {
  const user = getUserFromRequest(request);
  if (!user) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "No autenticado" } }, { status: 401 });
  }
  const adminEmail = getAdminEmail(user);

  const { sensors } = readSensores(adminEmail);
  return NextResponse.json({ data: sensors });
}
