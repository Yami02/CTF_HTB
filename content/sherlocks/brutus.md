---
title: "Brutus"
date: 2024-08-12
type: "sherlocks"
difficulty: "Easy"
pwned: true
tags: ["dfir", "linux", "auth-logs", "ssh", "brute-force", "wtmp", "btmp"]
summary: "Análise de logs de autenticação Linux (auth.log, wtmp, btmp) para identificar ataque de força bruta SSH e acesso não autorizado."
machine_info:
  Tipo: "Blue Team / DFIR"
  Arquivos: "auth.log, wtmp"
  Ferramentas: "grep, awk, last, utmpdump"
---

## Contexto

Um servidor Linux reportou comportamento anômalo. Recebemos `auth.log` e o arquivo `wtmp` para análise. Precisamos identificar o atacante, o usuário comprometido e o horário do comprometimento.

## Task 1 — Quantas tentativas de força bruta?

```bash
$ grep "Failed password" auth.log | wc -l
2294
```

**2294 tentativas falhadas** em um curto período — brute force confirmado.

## Task 2 — IP do atacante

```bash
$ grep "Failed password" auth.log | \
  awk '{print $(NF-3)}' | \
  sort | uniq -c | sort -rn | head -5

   2294 65.2.161.68
      1 203.101.190.9
```

**IP principal:** `65.2.161.68`

## Task 3 — Usuário alvo

```bash
$ grep "Failed password" auth.log | \
  grep "65.2.161.68" | \
  awk '{print $9}' | \
  sort | uniq -c | sort -rn | head

   2294 root
```

O atacante estava tentando force brutar o usuário **root** via SSH.

## Task 4 — Quando o ataque começou?

```bash
$ grep "Failed password.*65.2.161.68" auth.log | head -1
Mar  6 06:31:31 ip-172-31-35-28 sshd[2327]: Failed password for root from 65.2.161.68
```

**Início:** 06 Mar 2024, 06:31:31 UTC

## Task 5 — Login bem-sucedido?

```bash
$ grep "Accepted password" auth.log
Mar  6 06:32:44 ip-172-31-35-28 sshd[2411]: Accepted password for root from 65.2.161.68 port 34782 ssh2
```

Sim! O atacante conseguiu o acesso às **06:32:44**, apenas 73 segundos após iniciar o brute force.

## Task 6 — Sessão do atacante (wtmp)

```bash
$ utmpdump wtmp | grep "65.2.161.68"
[7] [02549] [ts/1] [root    ] [pts/1       ] [65.2.161.68         ] [65.2.161.68    ] [2024-03-06T06:32:45,000000+0000]
[8] [02549] [    ] [        ] [pts/1       ] [0.0.0.0             ] [0.0.0.0        ] [2024-03-06T06:37:24,000000+0000]
```

**Duração da sessão:** 06:32:45 → 06:37:24 (≈ 5 minutos)

## Task 7 — Usuário criado pelo atacante

```bash
$ grep "new user" auth.log
Mar  6 06:34:18 ip-172-31-35-28 useradd[2600]: new user: name=cyberjunkie, UID=1002, GID=1002, home=/home/cyberjunkie
```

O atacante criou o usuário **cyberjunkie** às 06:34:18 como backdoor.

## Timeline Resumida

| Horário (UTC) | Evento |
|---------------|--------|
| 06:31:31 | Início do brute force (65.2.161.68) |
| 06:32:44 | Login bem-sucedido como root |
| 06:34:18 | Criação do usuário backdoor 'cyberjunkie' |
| 06:37:24 | Encerramento da sessão SSH |

## IOCs

- **IP atacante:** 65.2.161.68
- **Usuário backdoor:** cyberjunkie (UID 1002)
- **Duração da intrusão:** ~5 minutos
- **Vetor:** SSH brute force com senha correta obtida
