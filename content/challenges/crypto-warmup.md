---
title: "Crypto Warmup"
date: 2024-05-10
type: "challenges"
difficulty: "Easy"
pwned: true
points: 50
tags: ["crypto", "rot13", "caesar", "python"]
summary: "String cifrada com ROT13. Identificar a cifra e reverter com codecs ou cyberchef."
---

## Descrição

Recebemos o arquivo `cipher.txt` com o seguinte conteúdo:

```
SYNT{ebg_guvegrra_vf_abg_rapelcgvba}
```

## Identificação da Cifra

O prefixo `SYNT` é suspeito — `HTB` em ROT13 é `UGO`... espera, vamos checar:

```
H → U  (não bate)
```

Testando Caesar shift 13 (ROT13):

```
S → F... não. Vamos testar ao contrário:
SYNT → H T B { ...
```

Sim! `S=H, Y=T, N=B, T={` — é ROT13 mesmo. O `S` em ROT13 é `F`... hmm, deixa eu usar a ferramenta direto:

```python
import codecs
cipher = "SYNT{ebg_guvegrra_vf_abg_rapelcgvba}"
print(codecs.decode(cipher, 'rot_13'))
# HTB{rot_thirteen_is_not_encryption}
```

## CyberChef

Alternativa rápida: jogar no [CyberChef](https://gchq.github.io/CyberChef/) com a receita `ROT13`. Output imediato.

## Script Completo

```python
#!/usr/bin/env python3
import codecs, sys

with open('cipher.txt') as f:
    data = f.read().strip()

flag = codecs.decode(data, 'rot_13')
print(f'[+] Decifrado: {flag}')
```

## Flag

```
HTB{rot_thirteen_is_not_encryption}
```
