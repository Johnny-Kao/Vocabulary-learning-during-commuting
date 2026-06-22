const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
  'Access-Control-Allow-Headers': 'Authorization, Content-Type',
};

function displayName(pw) {
  return pw.charAt(0).toUpperCase() + pw.slice(1);
}

async function getPeerInfo(env, selfPw, lang) {
  const validUsers = (env.VALID_PASSWORDS || '').split(',').map(p => p.trim()).filter(Boolean);
  const peer = validUsers.find(u => u !== selfPw);
  if (!peer) return {};
  const peerLang = lang === 'fr' ? 'de' : 'fr';
  const peerData = await env.PROGRESS_KV.get(`${peer}:${peerLang}`, 'json');
  return {
    peerName: displayName(peer),
    peerCount: peerData?.knownIds?.length || 0,
    peerLang,
  };
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    if (url.pathname !== '/progress') {
      return new Response('Not found', { status: 404, headers: CORS });
    }

    const pw = (request.headers.get('Authorization') || '').replace('Bearer ', '').trim();
    const validUsers = new Set((env.VALID_PASSWORDS || '').split(',').map(p => p.trim()).filter(Boolean));
    if (!pw || !validUsers.has(pw)) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    const lang = url.searchParams.get('lang') === 'de' ? 'de' : 'fr';
    const key = `${pw}:${lang}`;

    if (request.method === 'GET') {
      const data = await env.PROGRESS_KV.get(key, 'json');
      const peerInfo = await getPeerInfo(env, pw, lang);
      return new Response(JSON.stringify({
        ...(data ?? { lastIndex: 0, knownIds: [] }),
        ...peerInfo,
      }), {
        headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    if (request.method === 'PUT') {
      const body = await request.json().catch(() => ({}));
      await env.PROGRESS_KV.put(key, JSON.stringify({
        lastIndex: Number(body.lastIndex) || 0,
        knownIds: Array.isArray(body.knownIds) ? body.knownIds : [],
        updatedAt: new Date().toISOString(),
      }));
      const peerInfo = await getPeerInfo(env, pw, lang);
      return new Response(JSON.stringify({ ok: true, ...peerInfo }), {
        headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    return new Response('Method not allowed', { status: 405, headers: CORS });
  },
};
