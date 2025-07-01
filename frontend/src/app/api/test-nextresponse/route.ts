import { NextRequest, NextResponse } from 'next/server';

// Simple test to verify NextResponse works
export async function GET() {
  return NextResponse.json({ message: 'Test successful' });
}
