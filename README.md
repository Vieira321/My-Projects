# My Projects

A curated portfolio of academic and personal projects, organised by domain. My focus is **security engineering** (PKI, vulnerability assessment, applied cryptography), with a secondary track in **applied AI**.

Each project is self‑contained, documented, and reproducible — open any folder and its local `README.md` explains what it does, what it demonstrates, and how to run it. Where a written report exists, it is included as a PDF inside the project's `report/` folder.

---

## Table of Contents

- [Security](#security)
  - [Empirical Evaluation of Security Scanners for Docker Containers](#empirical-evaluation-of-security-scanners-for-docker-containers)
  - [PKI with mutual TLS (OpenSSL · NGINX · Flask)](#pki-with-mutual-tls-openssl--nginx--flask)
  - [Caesar Cipher Toolkit (Python)](#caesar-cipher-toolkit-python)
- [AI](#ai)
  - [CEREBRO — AI-Driven Secure Installer](#cerebro--ai-driven-secure-installer)
  - [Second Brain](#second-brain)
- [Games](#games)
  - [Connect Four — 3D (Three.js)](#connect-four--3d-threejs)
- [Repository Structure](#repository-structure)
- [License](#license)

---

## Security

### Empirical Evaluation of Security Scanners for Docker Containers

A comparative **empirical evaluation of four container vulnerability scanners** — **Trivy, Grype, Snyk, and Docker Scout** — using the **Goal‑Question‑Metric (GQM)** methodology over ten Docker images with distinct risk profiles (clean baselines, EOSL systems, and images carrying Shellshock, SambaCry, Log4Shell, Spring4Shell, and Confluence RCE).

The study quantifies real scanner blind spots: a **0% detection rate for Shellshock across all four tools** (source‑compiled software is invisible to metadata scanning), Docker Scout reporting **zero CVEs on EOSL Debian** while finding 848 on Ubuntu 16.04, and a **6.5× spread in vulnerability counts for the same image** (140 vs. 918). It closes with use‑case recommendations and per‑tool performance (Trivy fastest at 4.39 s; Snyk slowest at 19.81 s).

**Demonstrates:** GQM empirical methodology · hands‑on use of Trivy/Grype/Snyk/Docker Scout · reproducible vulnerable environments with Docker + Vulhub · JSON output parsing and metric analysis in Python
**Tech:** Docker · Trivy · Grype · Snyk · Docker Scout · Vulhub · Python
**Details:** [`security/vulnerability-scanner-evaluation/`](./security/vulnerability-scanner-evaluation/) · report included

---

### PKI with mutual TLS (OpenSSL · NGINX · Flask)

A full **Public Key Infrastructure** built from scratch: a self‑signed **Root CA**, a subordinate **Intermediate CA** that issues end‑entity certificates, and an **NGINX** server enforcing **mutual TLS (mTLS)** — only clients with a valid certificate signed by the chain reach the backend **Flask** app. The certificate lifecycle (issue, **revoke** with CRLs, renew, reissue) is fully scripted behind an interactive menu.

**Demonstrates:** two‑tier CA / trust‑chain design · X.509 + CRL management · mTLS client authentication · security automation in Bash/OpenSSL
**Tech:** Bash · OpenSSL · NGINX · Flask · X.509 · CRL · Linux
**Details:** [`security/pki-mtls-openssl-nginx/`](./security/pki-mtls-openssl-nginx/) · report included

---

### Caesar Cipher Toolkit (Python)

A command‑line cryptography toolkit implementing classic substitution ciphers and frequency analysis from scratch (no crypto libraries): a letter‑frequency histogram, the Caesar shift cipher, a scrambled‑alphabet cipher, and a dual‑key even/odd file cipher.

**Demonstrates:** symmetric ciphers from first principles · frequency analysis · key generation and modular arithmetic
**Tech:** Python 3 (standard library only)
**Details:** [`security/caesar-cipher/`](./security/caesar-cipher/)

---

## AI

### CEREBRO — AI‑Driven Secure Installer

A natural‑language software installer for Windows: you type *"install Discord"* and an **LLM agent** maps it to the right package, while a multi‑stage pipeline **verifies the installer's source before anything runs** (registered‑domain / trusted‑CDN checks that block unverified third‑party hosts), then hands control back to you to configure the install yourself.

**Demonstrates:** LLM agent design with structured (JSON‑schema) output · supply‑chain trust verification (eTLD+1 domain checks) · human‑in‑the‑loop safety gates · Windows/winget automation
**Tech:** Python · tkinter · Anthropic Claude API · winget
**Details:** [`ai/cerebro-secure-installer/`](./ai/cerebro-secure-installer/)

### Second Brain
> _A personal knowledge system that links notes into an interconnected graph (Karpathy "LLM Wiki" pattern). The published version contains the engine (ingestion code, schema, templates) and example notes only — no private content. README and code pending — being added._

Lives in [`ai/second-brain/`](./ai/second-brain/).

---

## Games

### Connect Four — 3D (Three.js)

A browser‑based **Connect Four** rendered in 3D with Three.js — full game loop, gravity, turn switching, and 4‑in‑a‑row win detection across all directions, over a glTF scene with custom textures and HDR lighting.

**Demonstrates:** real‑time 3D scene setup · clean separation of game logic from rendering · directional win‑detection algorithm
**Tech:** JavaScript (ES modules) · Three.js · glTF
**Details:** [`games/connect-four-3d/`](./games/connect-four-3d/)

---

## Repository Structure

```
My-Projects/
├── README.md                         # this portfolio index
├── LICENSE · .gitignore · .gitattributes
│
├── security/
│   ├── vulnerability-scanner-evaluation/   # empirical scanner evaluation (+ report)
│   ├── pki-mtls-openssl-nginx/             # PKI + mutual TLS (+ report, scripts)
│   └── caesar-cipher/                      # Python cipher toolkit
│
├── ai/
│   ├── cerebro-secure-installer/           # AI natural-language installer + supply-chain checks
│   └── second-brain/                       # note-graph knowledge system (engine only)
│
└── games/
    └── connect-four-3d/                    # Three.js 3D Connect Four
```

## License

Released under the [MIT License](./LICENSE).
