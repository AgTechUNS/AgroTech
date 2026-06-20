import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(null, { status: 204 });
}
