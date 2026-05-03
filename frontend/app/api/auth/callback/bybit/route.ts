import { NextRequest, NextResponse } from 'next/server';

// This MUST be dynamic to handle OAuth callbacks
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  
  console.log('📥 OAuth callback received:', { code: code?.slice(0, 20), state });
  
  if (!code) {
    return NextResponse.redirect(
      new URL('/dashboard?error=no_code', request.url)
    );
  }
  
  // Forward to Python backend
  try {
    const response = await fetch('http://127.0.0.1:8080/api/auth/callback/bybit', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    
    if (data.success) {
      return NextResponse.redirect(
        new URL(`/dashboard?connected=bybit&balance=${data.balance}`, request.url)
      );
    } else {
      return NextResponse.redirect(
        new URL(`/dashboard?error=${data.error}`, request.url)
      );
    }
  } catch (error) {
    console.error('❌ Callback error:', error);
    return NextResponse.redirect(
      new URL('/dashboard?error=connection_failed', request.url)
    );
  }
}
