---
title: "Crypto Warmup"
date: 2024-05-10
type: "challenges"
difficulty: "Easy"
pwned: true
points: 50
tags: ["crypto", "caesar", "rot13", "base64"]
summary: "Challenge de criptografia básica — ROT13, Base64 e Caesar cipher em sequência."
---

## Análise

Recebemos uma string cifrada:

```
SYNT{ebg_guvegrra_vf_abg_rapelcgvba}
```

## Solução

É ROT13!

```python
import codecs
cipher = "SYNT{ebg_guvegrra_vf_abg_rapelcgvba}"
print(codecs.decode(cipher, 'rot13'))
# HTB{rot_thirteen_is_not_encryption}
```

## Flag

```
HTB{rot_thirteen_is_not_encryption}
```
