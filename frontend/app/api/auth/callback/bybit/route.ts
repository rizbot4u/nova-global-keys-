import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  if (!code) return NextResponse.json({ error: 'No code provided' }, { status: 400 });

  // FIXED: Use port 8081 instead of 8080
const response = await fetch(`http://127.0.0.1:8081/api/auth/callback/bybit?code=${code}&state=${state}`);

  if (response.ok) {
    // Get session data from response
    const data = await response.json();
    
    // Redirect to dashboard with session
    return NextResponse.redirect(new URL(`/dashboard?session=${data.session_id || 'success'}`, request.url));
  }

  return NextResponse.json({ error: 'Backend failed to verify code' }, { status: 500 });
}
