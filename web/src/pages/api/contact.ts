export const prerender = false;

import type { APIRoute } from 'astro';

const DISCORD_WEBHOOK_URL = import.meta.env.DISCORD_WEBHOOK_URL;

function escape(s: string, max = 1000): string {
  return s.slice(0, max).replace(/[`@]/g, ' ');
}

export const POST: APIRoute = async ({ request, clientAddress }) => {
  try {
    const form = await request.formData();

    if (form.get('website')) {
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    }

    const name = String(form.get('name') || '').trim();
    const email = String(form.get('email') || '').trim();
    const message = String(form.get('message') || '').trim();

    if (!message || message.length < 5) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Message too short' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } },
      );
    }
    if (message.length > 4000) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Message too long' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } },
      );
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Invalid email' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } },
      );
    }

    if (!DISCORD_WEBHOOK_URL) {
      console.error('DISCORD_WEBHOOK_URL is not set');
      return new Response(
        JSON.stringify({ ok: false, error: 'Server not configured' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } },
      );
    }

    const ip = clientAddress || 'unknown';
    const ua = request.headers.get('user-agent') || 'unknown';

    const content =
      `**New contact form submission**\n` +
      `**Name:** ${escape(name || '(none)', 200)}\n` +
      `**Email:** ${escape(email || '(none)', 200)}\n` +
      `**IP:** ${escape(ip, 100)}\n` +
      `**UA:** ${escape(ua, 300)}\n` +
      `**Message:**\n${escape(message, 1800)}`;

    const discordRes = await fetch(DISCORD_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content,
        allowed_mentions: { parse: [] },
      }),
    });

    if (!discordRes.ok) {
      console.error('Discord webhook failed:', discordRes.status, await discordRes.text());
      return new Response(
        JSON.stringify({ ok: false, error: 'Failed to deliver' }),
        { status: 502, headers: { 'Content-Type': 'application/json' } },
      );
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    console.error('contact handler error:', err);
    return new Response(
      JSON.stringify({ ok: false, error: 'Server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } },
    );
  }
};
