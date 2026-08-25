---
title: "Baby RE"
date: 2024-03-15
type: "challenges"
difficulty: "Easy"
pwned: true
points: 30
tags: ["reverse-engineering", "strings", "binary", "linux"]
summary: "Binário ELF 64-bit que compara a entrada do usuário com uma string hardcoded. Flag visível com strings."
---

## Reconhecimento

```bash
$ file baby_re
baby_re: ELF 64-bit LSB executable, x86-64, dynamically linked

$ chmod +x baby_re && ./baby_re
Insira a flag: teste
Errado!
```

## Análise Estática

Primeiro passo: `strings` no binário para ver o que tem lá:

```bash
$ strings baby_re
/lib64/ld-linux-x86-64.so.2
puts
scanf
strcmp
Insira a flag:
Correto!
Errado!
HTB{str1ngs_4r3_y0ur_fr13nds}
```

A flag tava escondida em texto puro dentro do binário — sem obfuscação nenhuma.

## Verificação com ltrace

Só para confirmar, `ltrace` mostra a chamada ao `strcmp`:

```bash
$ ltrace ./baby_re
Insira a flag: qualquer_coisa
strcmp("qualquer_coisa", "HTB{str1ngs_4r3_y0ur_fr13nds}") = -1
puts("Errado!")
```

## Script Python

```python
import subprocess

output = subprocess.check_output(['strings', 'baby_re']).decode()
for line in output.splitlines():
    if line.startswith('HTB{'):
        print(f'[+] Flag: {line}')
        break
```

## Flag

```
HTB{str1ngs_4r3_y0ur_fr13nds}
```
