import { NextResponse } from 'next/server';

/**
 * Stub for navbar unread notification count.
 * Returns 0 until a real notifications backend exists.
 * Avoids 404 and console noise on every page load.
 */
export async function GET() {
  return NextResponse.json({ count: 0 });
}
