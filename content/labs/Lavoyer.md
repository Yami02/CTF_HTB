---
title: "Lavoyer"
date: 2026-10-10
type: "labs"
difficulty: "Hard"
pwned: true
os: "Linux"
tags: ["linux", "rdp", "wifi", "mac80211_hwsim", "tshark", "sniffing", "craft-cms", "yii2", "rce", "cups", "cve-2026-34990", "privesc"]
summary: "Cadeia multi-estágio: RDP num jump box de aeroporto, sniffing de WiFi aberta (texto claro) para credenciais, Craft CMS 5.9.8 -> RCE como aporter, e CUPS rodando como root para escalar via sudoers."
machine_info:
  IP: "10.129.109.82"
  OS: "Linux (Ubuntu / ambiente simulado)"
  Dificuldade: "Hard"
  Vetor inicial: "RDP contractor -> sniffing WiFi aberta (TShark)"
  Privesc: "CUPS 2.4.16 como root (CVE-2026-34990) -> /etc/sudoers.d/"
  Portas principais: "22/tcp (SSH), 3389/tcp (RDP)"
---

## Reconhecimento

```bash
$ nmap -A -T5 10.129.109.82
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH 9.6p1 (Ubuntu)
3389/tcp open  ms-wbt-server RDP (Microsoft Terminal Service)
```

RDP (3389) num host de aparência Linux chama atenção (`xrdp`/acesso remoto exposto). O fingerprint de OS ficou ambíguo (Linux 5.x / MikroTik RouterOS 7.x), típico de lab simulado. O nome de usuário `contractor` já era uma pista.

## Acesso Inicial — RDP como `contractor`

SSH indisponível para a conta `contractor`; acesso via RDP à workstation `airside-ws01`.

```bash
$ xfreerdp /v:10.129.109.82 /u:contractor /p:'Contractor2026!' /cert:ignore /dynamic-resolution
```

- `/cert:ignore` — ignora validação do certificado TLS (comum em labs).
- `/dynamic-resolution` — ajusta a resolução à janela.

A conta possui **`sudo` irrestrito** na workstation — base para a enumeração de rede seguinte.

## Enumeração de Rede — WiFi simulada

```bash
contractor@airside-ws01:~$ ip link
wlan2   UP / LOWER_UP   02:00:00:00:02:00   # associada
wlan3   DOWN / NO-CARRIER 02:00:00:00:03:00 # livre
eth0@if11 UP            00:16:3e:83:ea:41   # veth do container

contractor@airside-ws01:~$ iw dev
phy#2  wlan2  managed  associada - canal 6 (2437 MHz)
phy#3  wlan3  managed  sem canal (livre p/ monitor)
```

Os MACs `02:00:00:00:0X:00` são a assinatura do driver `mac80211_hwsim` (wireless simulado). A `wlan2` já está associada no **canal 6** (rede aberta "HTB International"); a `wlan3` está livre → candidata a **monitor mode**.

## Portal Cativo — pista do portal interno

Conectado à WiFi aberta, o portal cativo (`http://wifi.international.htb/`) traz um aviso para staff: o portal de funcionários "HTB Airways Miles" está acessível na rede de passageiros em:

```
http://portal.international.htb/miles/
```

O aviso pede logins periódicos → há **tráfego de autenticação de outros usuários em HTTP numa rede aberta**. Cenário perfeito para captura passiva.

## Captura de Credenciais — monitor mode + TShark

Monitor mode na `wlan3`, travada no **mesmo canal da `wlan2` (6)**:

```bash
$ sudo ip link set wlan3 down
$ sudo iw dev wlan3 set type monitor
$ sudo ip link set wlan3 up
$ sudo iw dev wlan3 set channel 6
$ iw dev wlan3 info        # confirma: type monitor, channel 6
```

> Ponto crítico: se o monitor não estiver no mesmo canal da rede alvo, nenhum frame é capturado.

Sniffing passivo dos POST (rede aberta + HTTP = plaintext):

```bash
$ sudo tshark -i wlan3 -Y 'http.request.method == "POST"' -T fields -e http.host -e http.file_data
portal.international.htb  757365726e616d653d6a656e6e792670617373776f72643d466c316768744465636b3230323621
```

Decodificado do hex:

```
username=jenny&password=Fl1ghtDeck2026!
```

A captura completa confirmou `POST /miles/login.php` com `User-Agent: curl/8.5.0` — login automatizado/periódico, o que explica a repetição das credenciais no tráfego.

**🔑 Credenciais:** `jenny` / `Fl1ghtDeck2026!`

## Craft CMS — login como `jenny`

As credenciais são reutilizadas no painel do **Craft CMS 5.9.8** (Solo). Conta `jenny` (`id=2`, `admin=false`, `allowAdminChanges=false`) → acesso administrativo **mas limitado**. CP trigger em `/admin`.

Recuperação de sessão por curl (útil quando a máquina reinicia e troca de IP, destruindo a sessão do servidor, mas as credenciais não mudam):

```bash
# 1. CSRF inicial + cookie de sessão
$ curl -s -c /tmp/cj.txt 'http://portal.international.htb/admin/login' -o /tmp/login.html
$ TOKEN=$(grep -oP 'csrfTokenValue":"\K[^"]+' /tmp/login.html)

# 2. Login reusando/atualizando o jar
$ curl -s -b /tmp/cj.txt -c /tmp/cj.txt \
    'http://portal.international.htb/index.php?p=admin/actions/users/login' \
    -H 'X-Requested-With: XMLHttpRequest' -H 'Accept: application/json' \
    --data-urlencode "loginName=jenny" \
    --data-urlencode "password=Fl1ghtDeck2026!" \
    --data-urlencode "CRAFT_CSRF_TOKEN=$TOKEN"
```

> Cookies do Craft/Yii: a sessão depende de `CraftSessionId`, `<hash>_identity` e `<hash>_username`; o `CRAFT_CSRF_TOKEN` é pareado com a sessão e precisa ser atualizado junto.

## Craft CMS → RCE → shell como `aporter`

> *Etapa descrita em alto nível, sem detalhes de exploração reproduzíveis.*

A partir do acesso limitado, uma vulnerabilidade de **behavior injection no Yii2** (framework do Craft) permite instanciar classes/métodos arbitrários, culminando em **RCE como a conta do servidor web**. Com execução de comando:

- Leitura do `.env` da aplicação → **Craft security key**.
- O banco do CMS contém uma **credencial criptografada** da conta `aporter`.
- Segredo criptografado **e** chave de decriptação no mesmo host → a senha é recuperada com a função nativa de decrypt do Craft/Yii.

Reverse shell recebido no listener (rodando no `airside-ws01`):

```bash
contractor@airside-ws01:/tmp$ nc -lnvp 4448
Connection received on 10.13.37.10 36434
```

Shell no host `portal` (`10.13.37.10`). **🚩 User flag** em `/home/aporter/user.txt`.

## Escalação de Privilégio — CUPS → root

> *Etapa descrita em alto nível, sem detalhes de exploração reproduzíveis.*

**Enumeração:** CUPS 2.4.16 rodando **como root** (daemon ativo localmente); `aporter` sem sudo nem caminho óbvio de escalonamento.

**Vulnerabilidade — CVE-2026-34990:** um usuário local captura um token de autorização local do CUPS e o abusa para criar uma impressora persistente apontando para uma URI `file://`. Imprimir pela fila maliciosa faz o daemon (como root) **escrever conteúdo controlado em um arquivo arbitrário**.

**Primitiva:** a escrita arbitrária como root é direcionada a `/etc/sudoers.d/`, criando uma regra que concede `sudo` sem senha a `aporter`:

```
[*] sudo -n id -> uid=0(root) gid=0(root) groups=0(root)
[+] ROOT via sudoers
```

```bash
root@portal:~# cat root.txt
e3e4fa22d01d74b6dc203a1957457631
```

## Attack Path — Resumo

| # | Etapa | Resultado |
|---|-------|-----------|
| 1 | Nmap | SSH (22) + RDP (3389) |
| 2 | RDP `contractor` | shell em `airside-ws01` (sudo) |
| 3 | Enum wireless (`mac80211_hwsim`) | WiFi aberta "HTB International" |
| 4 | Portal cativo | pista do portal `/miles/` em HTTP |
| 5 | Monitor mode + TShark | credenciais `jenny` / `Fl1ghtDeck2026!` |
| 6 | Login Craft CMS 5.9.8 | acesso admin limitado |
| 7 | RCE (Yii2) → decrypt `.env` | shell como `aporter` + **user flag** |
| 8 | CUPS (CVE-2026-34990) → sudoers | **root** + **root flag** |

## Flags

```
user.txt → /home/aporter/user.txt
root.txt → e3e4fa22d01d74b6dc203a1957457631
```

## Lições / Vulnerabilidades

- **WiFi aberta + HTTP = texto claro.** Rede sem criptografia + portal sem TLS → captura passiva trivial de autenticação alheia.
- **Reuso de credenciais.** A senha capturada no portal de milhas valia no painel do CMS.
- **Segredo + chave no mesmo host.** Guardar material criptografado e chave de decriptação juntos anula a proteção.
- **Serviço privilegiado com escrita de arquivos.** Daemon como root capaz de escrever em caminhos arbitrários (CUPS) é vetor clássico de privesc, aqui direcionado a `/etc/sudoers.d/`.

## Referências

- Craft CMS — segurança: https://craftcms.com/knowledge-base/securing-craft
- Yii Framework — advisories: https://github.com/yiisoft/yii2/security
- CUPS — projeto oficial: https://openprinting.github.io/cups/
