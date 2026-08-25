# Baby Frame — Writeup

**Flag:** `HTB{901f426f6ab1938d83bf6184f8aa0307}`

## Resumo do desafio

O desafio expõe um serviço TCP que simula um satélite falando o protocolo **CCSDS**
(o padrão real usado por agências espaciais tipo NASA/ESA para comunicação com naves).
O objetivo era montar um pacote de comando bem formado e enviar pelo protocolo certo
até o "satélite" responder com a flag.

O `client.py` fornecido já dava a estrutura esperada:

```python
def generate_space_packet(apid, packet_count, payload) -> bytes: ...
def generate_tc_frame(spacecraft_id, virtual_channel_id, tc_packet_count, payload) -> bytes: ...
```

Ou seja, dois "envelopes" um dentro do outro:

```
Transfer Frame (TC)
└── Space Packet
    └── payload (a mensagem de verdade)
```

## Passo 1 — Entender o formato do Space Packet

O Space Packet Protocol (CCSDS 133.0-B-2) define um cabeçalho fixo de **6 bytes**
na frente de qualquer payload:

| Campo | Tamanho | O que é |
|---|---|---|
| Version + Type + Sec.Header Flag + APID | 2 bytes | identifica de qual "aplicação" o pacote é (APID) |
| Sequence Flags + Sequence Count | 2 bytes | número do pacote na sequência |
| Packet Data Length | 2 bytes | tamanho do payload **menos 1** |

Montamos esse cabeçalho com operações de bit simples (`<<`, `|`) e empacotamos
com `struct.pack(">HHH", ...)` (big-endian, três campos de 16 bits).

## Passo 2 — Entender o formato do TC Transfer Frame

O TC Transfer Frame (CCSDS 232.0-B-3) é o "envelope de transporte" — tem seu
próprio cabeçalho de **5 bytes**, que carrega:

- **Spacecraft ID (SCID)** — identifica a nave (`12`, dado no enunciado)
- **Virtual Channel ID (VCID)** — canal lógico dentro do link (`3`, dado no enunciado)
- **Frame Length** — tamanho total do frame **menos 1**
- Flags de controle (bypass, control command) e um número de sequência

Esse cabeçalho de 5 bytes vem seguido diretamente do Space Packet inteiro (sem
nenhum byte extra no meio).

## Passo 3 — Erro inicial e correção

O `client.py` original tinha um bug: montava o `frame` (que já contém o
`space_packet` dentro) e depois enviava `frame + space_packet` — duplicando o
pacote sem necessidade. Corrigimos pra enviar só `frame`.

## Passo 4 — Testando contra o servidor

Com o SCID, VCID e APID do enunciado (`12`, `3`, `42`) e um payload de teste
(`TEST_PAYLOAD`), o servidor sempre respondia **vazio e fechava a conexão**.

Pra descobrir por quê, fizemos um teste de diagnóstico: mandamos vários frames
"vazios" (nada, lixo, texto) e comparamos o tempo/comportamento de resposta.
Isso confirmou que:

- Sem enviar nada → o servidor **espera** (não fecha)
- Enviando um frame válido → o servidor **fecha ativamente (EOF)**

Ou seja, o parser estava processando o frame e rejeitando alguma coisa
especificamente — não era um problema de timing ou de protocolo incompleto.

## Passo 5 — A pista que faltava: o payload certo

O enunciado revelou o detalhe que faltava: o serviço esperava um pacote
contendo o payload exato `HEALTHCHECK` (um "diagnóstico" de saúde da nave,
não um valor de teste qualquer).

Trocamos o payload de `TEST_PAYLOAD` para `HEALTHCHECK`, mantendo:

```python
spacecraft_id = 12
virtual_channel_id = 3
apid = 42
packet_count = 0
```

## Passo 6 — Sucesso

Ao enviar o frame com o payload correto, o servidor respondeu imediatamente:

```
SPACECRAFT: HTB{901f426f6ab1938d83bf6184f8aa0307}
```

## O que isso ensina

O desafio simula bem um cenário real de segurança em sistemas espaciais:
o protocolo CCSDS **não tem autenticação embutida por padrão** — qualquer
cliente que monte o frame corretamente (SCID/VCID/APID certos) e mande o
comando esperado consegue "falar" com o subsistema. A dificuldade do CTF
não estava em quebrar criptografia, e sim em **entender o formato binário
do protocolo** (dois cabeçalhos aninhados, cálculo de tamanho "N-1", campos
de bits) e em descobrir, por tentativa estruturada, qual comando o serviço
esperava.

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
