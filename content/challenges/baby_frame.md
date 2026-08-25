---
title: "Baby Frame"
date: 2026-08-25
type: "challenges"
difficulty: "Easy"
pwned: true
points: 30
tags: ["ccsds", "satellite", "protocol", "networking", "pwntools"]
summary: "Serviço TCP simula um satélite falando CCSDS. É preciso montar manualmente um Space Packet dentro de um TC Transfer Frame, com SCID/VCID/APID corretos e o payload esperado, para disparar a resposta de diagnóstico."
---

## Reconhecimento

O desafio fornece um `client.py` esqueleto e um endpoint remoto:

```bash
$ cat client.py
from pwn import log, remote, process

def generate_space_packet(apid: int, packet_count: int, payload: bytes) -> bytes:
    ...
    return packet

def generate_tc_frame(spacecraft_id: int, virtual_channel_id: int,
                       tc_packet_count: int, payload: bytes) -> bytes:
    ...
    return frame

def main():
    HOST = ...
    PORT = ...
    space_packet = generate_space_packet(apid=42, packet_count=0, payload=b"TEST_PAYLOAD")
    frame = generate_tc_frame(spacecraft_id=12, virtual_channel_id=3,
                               tc_packet_count=0, payload=space_packet)
    payload = frame + space_packet
    r = remote(HOST, PORT)
    r.send(payload)
```

Os nomes das funções e o parâmetro `spacecraft_id`/`virtual_channel_id`/`apid` deixam
claro que o desafio é sobre **CCSDS** — o padrão de comunicação usado por agências
espaciais (NASA, ESA etc.) para falar com satélites via link de rádio.

## Análise do protocolo

CCSDS define duas camadas relevantes aqui:

- **Space Packet Protocol** (CCSDS 133.0-B-2) — o "payload de aplicação", com um
  cabeçalho fixo de 6 bytes contendo APID, contador de sequência e tamanho.
- **TC Space Data Link Protocol** (CCSDS 232.0-B-3/B-4) — o "envelope de transporte"
  (Transfer Frame), com cabeçalho fixo de 5 bytes contendo Spacecraft ID (SCID),
  Virtual Channel ID (VCID) e tamanho total do frame.

Um Space Packet nunca trafega sozinho — ele vai encapsulado dentro de um Transfer
Frame:

```
Transfer Frame
├── Primary Header (5 bytes) — SCID, VCID, frame length...
└── Transfer Frame Data Field
    └── Space Packet
        ├── Primary Header (6 bytes) — APID, sequence, length...
        └── User Data Field (o payload de verdade)
```

Ambos os cabeçalhos usam campos de bits (não bytes inteiros) e uma convenção comum
em protocolos espaciais: campos de "tamanho" armazenam **N-1**, não N.

### Bug identificado no skeleton

```python
payload = frame + space_packet
```

`frame` já contém o `space_packet` dentro dele — essa linha duplicava o pacote
sem necessidade. Corrigido para `r.send(frame)`.

## Implementação

```python
import struct

def generate_space_packet(apid, packet_count, payload, packet_type=1, seq_flags=0b11):
    version = 0
    sec_hdr_flag = 0
    word0 = (version << 13) | (packet_type << 12) | (sec_hdr_flag << 11) | (apid & 0x7FF)
    word1 = (seq_flags << 14) | (packet_count & 0x3FFF)
    data_length = len(payload) - 1
    header = struct.pack(">HHH", word0, word1, data_length)
    return header + payload


def generate_tc_frame(scid, vcid, seq, payload, bypass=0, cc=0):
    tfvn, spare = 0, 0
    frame_length = 5 + len(payload) - 1
    value = (tfvn & 0x3) << 38
    value |= (bypass & 0x1) << 37
    value |= (cc & 0x1) << 36
    value |= (spare & 0x3) << 34
    value |= (scid & 0x3FF) << 24
    value |= (vcid & 0x3F) << 18
    value |= (frame_length & 0x3FF) << 8
    value |= (seq & 0xFF)
    return value.to_bytes(5, "big") + payload
```

## Diagnóstico de conexão

Com SCID=12, VCID=3, APID=42 e payload `TEST_PAYLOAD`, o servidor sempre fechava
a conexão sem responder nada. Um teste comparativo (mandar nada / lixo / o frame)
mostrou que o servidor **reagia ativamente** ao frame (fechava com EOF rápido),
diferente de "sem enviar nada" (onde ele ficava esperando). Isso indicou que o
parser processava o frame e rejeitava algo específico — não um problema de timing.

```bash
$ python3 client.py
[+] Opening connection to 154.57.164.72 on port 31255: Done
[+] Receiving all data: Done (0B)
[*] Server response: b''
```

O enunciado da fase seguinte revelou o detalhe que faltava: o payload esperado
não era um valor de teste qualquer, e sim o comando **`HEALTHCHECK`**.

## Verificação

```bash
$ python3 client.py
[DEBUG] Sent 0x16 bytes:
    00000000  00 0c 0c 15  00 10 2a c0  00 00 0a 48  45 41 4c 54  |····|··*·|···H|EALT|
    00000010  48 43 48 45  43 4b                                  |HCHE|CK|
[+] Receiving all data: Done (50B)
[DEBUG] Received 0x32 bytes:
    b'SPACECRAFT: HTB{901f426f6ab1938d83bf6184f8aa0307}\n'
```

## Script final

```python
import struct
from pwn import remote

HOST = "154.57.164.72"
PORT = 31255


def generate_space_packet(apid, packet_count, payload, packet_type=1, seq_flags=0b11):
    version = 0
    sec_hdr_flag = 0
    word0 = (version << 13) | (packet_type << 12) | (sec_hdr_flag << 11) | (apid & 0x7FF)
    word1 = (seq_flags << 14) | (packet_count & 0x3FFF)
    data_length = len(payload) - 1
    header = struct.pack(">HHH", word0, word1, data_length)
    return header + payload


def generate_tc_frame(scid, vcid, seq, payload, bypass=0, cc=0):
    tfvn, spare = 0, 0
    frame_length = 5 + len(payload) - 1
    value = (tfvn & 0x3) << 38
    value |= (bypass & 0x1) << 37
    value |= (cc & 0x1) << 36
    value |= (spare & 0x3) << 34
    value |= (scid & 0x3FF) << 24
    value |= (vcid & 0x3F) << 18
    value |= (frame_length & 0x3FF) << 8
    value |= (seq & 0xFF)
    return value.to_bytes(5, "big") + payload


def main():
    sp = generate_space_packet(apid=42, packet_count=0, payload=b"HEALTHCHECK")
    frame = generate_tc_frame(scid=12, vcid=3, seq=0, payload=sp)

    r = remote(HOST, PORT)
    r.send(frame)
    print(r.recvall(timeout=5).decode())


if __name__ == "__main__":
    main()
```
