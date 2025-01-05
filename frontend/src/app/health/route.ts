import { NextResponse } from 'next/server';

export async function GET() {
    console.log("GET /health");
    return NextResponse.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        backend_host: process.env.BACKEND_HOST,
    });
}