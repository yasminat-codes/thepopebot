#!/usr/bin/env node
/**
 * Ollama proxy — injects `think: false` into every chat/generate request.
 * Sits between thepopebot (LangChain ChatOpenAI) and Ollama.
 *
 * Usage: node proxy/ollama-proxy.js
 * thepopebot → port 11435 → this proxy → Ollama port 11434
 */

const http = require('http');

const OLLAMA_HOST = 'localhost';
const OLLAMA_PORT = 11434;
const PROXY_PORT = 11435;

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', chunk => (body += chunk));
  req.on('end', () => {
    let parsed = {};
    let newBody = body;

    // Inject think: false into chat and generate endpoints
    const isChatRequest =
      req.url.includes('/chat') || req.url.includes('/generate');

    if (isChatRequest && body) {
      try {
        parsed = JSON.parse(body);
        parsed.think = false;
        newBody = JSON.stringify(parsed);
      } catch (e) {
        // Non-JSON body — pass through unchanged
      }
    }

    const options = {
      hostname: OLLAMA_HOST,
      port: OLLAMA_PORT,
      path: req.url,
      method: req.method,
      headers: {
        ...req.headers,
        host: `${OLLAMA_HOST}:${OLLAMA_PORT}`,
        'content-length': Buffer.byteLength(newBody),
      },
    };

    const proxyReq = http.request(options, proxyRes => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', err => {
      console.error('Proxy error:', err.message);
      res.writeHead(502);
      res.end('Proxy error: ' + err.message);
    });

    proxyReq.write(newBody);
    proxyReq.end();
  });
});

server.listen(PROXY_PORT, () => {
  console.log(
    `Ollama proxy listening on :${PROXY_PORT} → Ollama :${OLLAMA_PORT} (think: false injected)`
  );
});
