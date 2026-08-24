---
title: "Baby RE"
date: 2024-03-15
type: "challenges"
difficulty: "Easy"
pwned: true
points: 30
tags: ["reverse-engineering", "binary", "python"]
summary: "Um binário simples de reversão que verifica uma string de entrada contra uma chave hardcoded."
---

## Descrição

Challenge de reverse engineering nível entry — perfeito pra quem tá começando.

## Análise Estática

```bash
$ file baby_re
baby_re: ELF 64-bit LSB executable, x86-64

$ strings baby_re | grep -i flag
Inserisci la flag: 
HTB{str1ngs_4r3_y0ur_fr13nds}
```

## Solução

A flag tava nos próprios strings do binário 😂

```python
import subprocess
out = subprocess.check_output(['strings', 'baby_re'])
for line in out.decode().split('\n'):
    if 'HTB' in line:
        print(line)
```

## Flag

```
HTB{str1ngs_4r3_y0ur_fr13nds}
```
