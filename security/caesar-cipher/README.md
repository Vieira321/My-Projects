# Caesar Cipher Toolkit (Python)

A command‑line cryptography toolkit built for a Programming Lab (*Laboratório de Programação*). It implements classic substitution ciphers and a simple cryptanalysis primitive entirely from scratch, with no cryptography libraries.

**Authors:** Diogo Vieira · João Monteiro · Jorge Pereira · Tiago Moreira

## Features

Selectable from an interactive menu:

1. **Letter‑frequency histogram** — counts letter occurrences in a text file and prints a bar histogram. This is the foundation of breaking substitution ciphers by frequency analysis.
2. **Caesar cipher** — encrypts/decrypts a phrase by shifting letters by a numeric key, using modular arithmetic to wrap around the alphabet.
3. **Scrambled‑alphabet cipher** — generates a random substitution key (a shuffled alphabet) and encodes/decodes text against it.
4. **Dual‑key file cipher** — encodes a text file by alternating **two** substitution alphabets across even/odd character positions, then decodes it back.

## How to run

```bash
python3 projeto.py
```

The program reads two sample files from the same directory:
- `TESTE.txt` — input for the frequency histogram (option 1)
- `ProjetoFile.txt` — input for the dual‑key file cipher (option 4)

**Dependencies:** none — Python 3 standard library only.
`matplotlib` is optional and only needed if you uncomment the graphical histogram block in option 1.

## Skills demonstrated

- Implementing symmetric substitution ciphers from first principles
- Frequency analysis as a cryptanalysis technique
- Random key generation and modular index arithmetic over an alphabet
- File I/O and a menu‑driven CLI
