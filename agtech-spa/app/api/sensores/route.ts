import { NextResponse } from "next/server";
import { readSensores } from "@/lib/data/store";

export async function GET() {
  const { sensors } = readSensores();
  return NextResponse.json({ data: sensors });
}
