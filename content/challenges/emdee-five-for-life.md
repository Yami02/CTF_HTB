---
title: "Emdee Five For Life"
date: 2024-04-03
type: "challenges"
difficulty: "Easy"
pwned: true
points: 20
tags: ["web", "python", "md5", "scripting", "requests"]
summary: "O servidor pede o MD5 de uma string aleatória. Rápido demais para fazer na mão — automação com requests + hashlib."
---

## Descrição

O site exibe uma string aleatória e pede para você enviar o MD5 dela. Simples... exceto que o tempo de resposta é de milissegundos — impossível fazer manualmente.

## Análise do Fluxo

```
GET /  → Exibe a string a ser hasheada
POST / com md5=<hash> → Valida e retorna a flag (se correto e rápido)
```

O servidor usa cookie de sessão para manter o estado, então precisamos usar `requests.Session`.

## Solução

```python
#!/usr/bin/env python3
import requests
import hashlib
from bs4 import BeautifulSoup

TARGET = "http://127.0.0.1:1337"

session = requests.Session()

# 1. GET para obter a string e o cookie de sessão
r = session.get(TARGET)
soup = BeautifulSoup(r.text, 'html.parser')

# A string está dentro de uma tag <h3>
string_to_hash = soup.find('h3').text.strip()
print(f"[*] String: {string_to_hash}")

# 2. Calcular MD5
md5 = hashlib.md5(string_to_hash.encode()).hexdigest()
print(f"[*] MD5: {md5}")

# 3. POST com o hash (mesma sessão = mesmo cookie)
r = session.post(TARGET, data={"hash": md5})
soup = BeautifulSoup(r.text, 'html.parser')

# Procurar a flag no response
if "HTB{" in r.text:
    import re
    flag = re.search(r'HTB\{[^}]+\}', r.text).group()
    print(f"[+] Flag: {flag}")
else:
    print("[-] Falhou:", soup.find('p').text if soup.find('p') else r.text[:200])
```

## Por que Session?

Sem `requests.Session()`, cada requisição usa cookies diferentes e o servidor não reconhece que o POST veio de quem fez o GET anterior.

## Flag

```
HTB{w3lc0m3_t0_sc1pt1ng}
```
