---
title: "noerror"
date: 2026-08-25
type: "challenges"
difficulty: "Easy"
pwned: false
points: 30
tags: ["ccsds", "satellite", "crc", "protocol", "pwntools"]
summary: "Evolução do desafio CCSDS anterior: o servidor agora valida o Frame Error Control Field (CRC-16) do TC Transfer Frame antes de aceitar o comando."
---

## Reconhecimento

Mesmo protocolo do desafio anterior (CCSDS Space Packet + TC Transfer Frame), mas
com uma restrição nova anunciada no enunciado:

> "the onboard system has transitioned into protected transmission mode [...]
> telemetry frames are now validated using the [...] Frame Error Control Field"

Ou seja: o frame que antes bastava montar com header + payload agora precisa de
um **CRC-16 (FECF)** anexado no final, calculado corretamente, ou o servidor
rejeita o pacote.

Payload alvo desta fase: `GIVE-ME-THE-FLAG`

## Análise — o que muda estruturalmente

```
Antes (sem FECF):
┌─────────────────────────┐
│ Primary Header (5 bytes)│
├─────────────────────────┤
│ Transfer Frame Data Field│
└─────────────────────────┘

Agora (com FECF):
┌─────────────────────────┐
│ Primary Header (5 bytes)│
├─────────────────────────┤
│ Transfer Frame Data Field│
├─────────────────────────┤
│ Frame Error Control Field│ (2 bytes, CRC-16)
└─────────────────────────┘
```

Duas consequências práticas:

1. O campo **Frame Length** do header passa a contar os 2 bytes extras do FECF.
2. É preciso implementar o algoritmo de CRC exatamente como a spec define.

## Especificação do CRC (CCSDS 232.0-B-4, seção 4.1.4)

```
FECF = [(X^16 · M(X)) + (X^(n-16) · L(X))] mod G(X)
```

Traduzindo pra parâmetros de implementação:

| Parâmetro | Valor |
|---|---|
| Polinômio gerador G(X) | X¹⁶ + X¹² + X⁵ + 1 → `0x1021` |
| Valor inicial (preset) | `0xFFFF` |
| XOR final | nenhum |
| Reflect in/out | nenhum |
| Escopo do cálculo | Primary Header + Data Field (sem incluir o próprio FECF) |

Isso corresponde ao algoritmo conhecido como **CRC-16/CCITT-FALSE**.

## Implementação

```python
import struct

def crc16_ccsds(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return struct.pack(">H", crc)


def generate_tc_frame(scid, vcid, seq, payload, bypass=0, cc=0, with_fecf=True):
    tfvn, spare = 0, 0
    fecf_len = 2 if with_fecf else 0
    frame_length = 5 + len(payload) + fecf_len - 1   # agora conta o FECF

    value = (tfvn & 0x3) << 38
    value |= (bypass & 0x1) << 37
    value |= (cc & 0x1) << 36
    value |= (spare & 0x3) << 34
    value |= (scid & 0x3FF) << 24
    value |= (vcid & 0x3F) << 18
    value |= (frame_length & 0x3FF) << 8
    value |= (seq & 0xFF)

    header_e_dados = value.to_bytes(5, "big") + payload
    frame = header_e_dados
    if with_fecf:
        frame += crc16_ccsds(header_e_dados)   # CRC sobre tudo, exceto ele mesmo
    return frame
```

## Verificação

> ⚠️ Seção pendente — colar aqui o hexdump enviado e a resposta do servidor assim
> que o script rodar com sucesso contra o host/porta ativos do desafio.

```bash
$ python3 client.py
[DEBUG] Sent 0x?? bytes:
    ...
[+] Receiving all data: ...
```

## Script final

```python
import struct
from pwn import remote

HOST = "154.57.164.82"
PORT = 30806


def generate_space_packet(apid, packet_count, payload, packet_type=1, seq_flags=0b11):
    version = 0
    sec_hdr_flag = 0
    word0 = (version << 13) | (packet_type << 12) | (sec_hdr_flag << 11) | (apid & 0x7FF)
    word1 = (seq_flags << 14) | (packet_count & 0x3FFF)
    data_length = len(payload) - 1
    header = struct.pack(">HHH", word0, word1, data_length)
    return header + payload


def crc16_ccsds(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return struct.pack(">H", crc)


def generate_tc_frame(scid, vcid, seq, payload, bypass=0, cc=0, with_fecf=True):
    tfvn, spare = 0, 0
    fecf_len = 2 if with_fecf else 0
    frame_length = 5 + len(payload) + fecf_len - 1

    value = (tfvn & 0x3) << 38
    value |= (bypass & 0x1) << 37
    value |= (cc & 0x1) << 36
    value |= (spare & 0x3) << 34
    value |= (scid & 0x3FF) << 24
    value |= (vcid & 0x3F) << 18
    value |= (frame_length & 0x3FF) << 8
    value |= (seq & 0xFF)

    header_e_dados = value.to_bytes(5, "big") + payload
    frame = header_e_dados
    if with_fecf:
        frame += crc16_ccsds(header_e_dados)
    return frame


def main():
    sp = generate_space_packet(apid=42, packet_count=0, payload=b"GIVE-ME-THE-FLAG")
    frame = generate_tc_frame(scid=12, vcid=3, seq=0, payload=sp, with_fecf=True)

    r = remote(HOST, PORT)
    r.send(frame)
    print(r.recvall(timeout=5).decode())


if __name__ == "__main__":
    main()
```

## Flag

```
(pendente — rodar o script e colar aqui a flag retornada pelo servidor)
```
