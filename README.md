```
                            ####                                                        ####
                             %#######                                                  #######
                             %## ######                                              #####%###
                             %##   ######                                          #####   ###
                             %##%     #####                                      #####     ###
                              ##%      %#####                                  #####       ###
                              ###        %#####                              #####         ##%
                              ###          #####                            #####         ###
                              ####          %####                          ####           ###
                               ###     %#     ####                        ####           ###%
                               ####     %##    ####                      ####     #      ###
                                ###       ##    ####                    ####    ##      ###
                                 ###       ##   ####                   ####    ##      ####
                                 ####       ##   ####                  ###    ##      ####
                                  %####      ##   ###                 ####   ##      ####
                                    ####     ###  ####                ###   ##     ####
                                      ####    ##   ###    #%####%#   ####  ##    ####%
                                       %####   #%  ### #################   #    ####
                                         #####     #####################      ####
                                            ###  #########################  ###%
                                                ###########################
                                               #############################%
                                              ###############################%
                                             ##################################
                                            ###################################
                                            ###% #########################  ####
                                            ###      ######%###########     ###
                                            ###        ######### ###        ###%
                                           %###          %########          ####
                                          %#####         ##########         #####
                                         ########      ######%######      ########
                                         #######    %#######    #######    #######
                                          %################     #################
                                            ###############%####%##############%
                                                     ##################
                                                ##  @##################  ##
                                                 ##  ###########%## ##  ###
                                                 ##   # ########@## #   ###
                                                 ###  %    ## ##       %##%
                                                 %######            ######
                                                   %######### ## #######
                                                      ################
                                                        ############
                                                          %%%##%%
```

<div align="center">

# 0xYami02 // 0xNihil

**Writeups & CTF Hacking Notes — HackTheBox**

[![Deploy Hugo site to Pages](https://github.com/Yami02/CTF_HTB/actions/workflows/hugo.yaml/badge.svg)](https://github.com/Yami02/CTF_HTB/actions/workflows/hugo.yaml)
[![Hugo](https://img.shields.io/badge/hugo-0.128.0-ff2d78?logo=hugo)](https://gohugo.io/)
[![Pages](https://img.shields.io/badge/pages-live-00ff99)](https://yami02.github.io/CTF_HTB/)

[🌐 Site ao vivo](https://yami02.github.io/CTF_HTB/) · [LinkedIn](https://www.linkedin.com/in/adalberto-nobre-neto/)

</div>

---

## Sobre

Repositório dos meus writeups de CTF do HackTheBox, publicado como um site estático
via **Hugo** + **GitHub Pages**. Tema cyberpunk custom (rosa/verde neon), com um
explorador de arquivos lateral no estilo VS Code para navegar entre categorias.

## Estrutura de conteúdo

```
content/
├── challenges/   # Challenges pontuais (crypto, web, pwn, RE, forense...)
├── labs/         # Máquinas (Linux/Windows/AD)
└── sherlocks/    # Sherlocks (DFIR / Blue Team)
```

Cada writeup é um arquivo Markdown com front matter (`difficulty`, `pwned`, `tags`,
`points`, `machine_info`, etc.) que alimenta os badges, filtros e o histórico
exibido na home.

## Stack

- **[Hugo](https://gohugo.io/)** `0.128.0` (extended) — gerador de site estático
- Tema custom em `themes/cyberpunk/` — sem dependências externas de JS/CSS além
  das fontes do Google (Orbitron, Share Tech Mono, Rajdhani)
- **GitHub Actions** (`.github/workflows/hugo.yaml`) — build e deploy automático
  para GitHub Pages a cada push em `main`

## Rodando localmente

```bash
# instale o Hugo extended (>= 0.128.0)
hugo server -D
```

O site sobe em `http://localhost:1313/CTF_HTB/`.

## Novo writeup

```bash
hugo new content/challenges/nome-do-challenge.md
# ou labs/ / sherlocks/, seguindo o front matter dos exemplos existentes
```

---

<div align="center">

`> whoami` — **0xYami02** // **0xNihil**

[GitHub](https://github.com/Yami02) · [HackTheBox](https://www.hackthebox.com) · [LinkedIn](https://www.linkedin.com/in/adalberto-nobre-neto/)

</div>
