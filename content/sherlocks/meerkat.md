---
title: "Meerkat"
date: 2024-06-01
type: "sherlocks"
difficulty: "Easy"
pwned: true
tags: ["dfir", "network", "pcap", "bonitoboss"]
summary: "Análise de tráfego de rede para identificar um ataque de força bruta e comprometimento de credenciais no Bonitoboss BPM."
---

## Contexto

A empresa recebeu alertas de atividade suspeita. Precisamos analisar os logs de rede e identificar o vetor de ataque.

## Análise do PCAP

```bash
$ wireshark meerkat.pcap
# Filtro: http.request.method == "POST"
```

Identificamos múltiplas tentativas de login no painel do **Bonitasoft BPM** (porta 8080).

## Extração de Credenciais

```bash
$ tshark -r meerkat.pcap -Y 'http.request.method == "POST"' \
  -T fields -e http.file_data | grep -i "username"
```

Credenciais encontradas:
- Username: `seb.broom@forela.co.uk`
- Senha: `g0vernm3nt`

## CVE Explorada

**CVE-2022-25237** — Bonitasoft Authentication Bypass + RCE

## Conclusão

O atacante usou credenciais padrão de uma wordlist conhecida e escalou para RCE via extensão de API não autenticada.
