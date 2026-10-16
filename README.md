# Diogo Vieira — Projects

**MSc in Computer Engineering (Cybersecurity and Systems Administration), ISEP.**
I work on **security engineering**: container security, PKI, vulnerability assessment and applied cryptography. I also build **applied AI** tools. This repository holds my MSc dissertation, my academic course projects and my personal projects, each in its own folder. Every project folder has its own `README.md` explaining what it does and how to run it. Where there is a written report, the PDF is in that project's `report/` folder.

---

## At a glance

| Project | Type | What it is | Highlight | Stack |
|---|---|---|---|---|
| ⭐ [**Dockerfile Refactorings: Detection and Effects**](#dockerfile-refactorings-detection-and-effects) | MSc thesis | MSc dissertation: a tool that detects Dockerfile refactorings in Git history and measures their effect on size, CVEs and maintainability | 100% detection over 49 commit pairs · CRITICAL CVEs 56 → 2 · 302 tests, 94% coverage | Python · Docker · Trivy · Hadolint |
| [**Container Scanner Evaluation**](#empirical-evaluation-of-security-scanners-for-docker-containers) | Academic | Empirical comparison of Trivy, Grype, Snyk and Docker Scout over 10 vulnerable images | Found a 0% Shellshock detection rate in all four tools | Docker · Trivy · Grype · Snyk |
| [**PKI with mutual TLS**](#pki-with-mutual-tls-openssl--nginx--flask) | Academic | Two-tier certificate authority enforcing client-certificate authentication in front of a web app | Full certificate lifecycle (issue, revoke, renew) scripted | OpenSSL · NGINX · Bash |
| [**Caesar Cipher Toolkit**](#caesar-cipher-toolkit-python) | Academic | Classic ciphers and frequency analysis built from scratch | No crypto libraries | Python |
| [**Connect Four 3D**](#connect-four--3d-threejs) | Academic | Browser game rendered in 3D | Directional win detection, logic separated from rendering | JavaScript · Three.js |
| [**CEREBRO**](#cerebro--ai-driven-secure-installer) | Personal | Natural-language software installer that verifies the download source before running anything | LLM agent with supply-chain trust checks | Python · Claude API · winget |
| [**Second Brain**](#second-brain--llm-maintained-knowledge-base) | Personal | AI agent that compiles raw notes into an interlinked Obsidian wiki | Rule schema plus lint workflow for an agentic compiler | Claude Code · Obsidian |

## Skills shown

| Area | Where |
|---|---|
| **Container security & DevSecOps**: vulnerability scanning, image hardening, Dockerfile linting | Dissertation · Scanner Evaluation |
| **Cryptography & PKI**: X.509, CRLs, mTLS, classic ciphers | PKI · Caesar Cipher |
| **Research methods**: Design Science Research, GQM, PRISMA literature review | Dissertation · Scanner Evaluation |
| **Software engineering**: modular Python architecture, pytest, CLI tools | Dissertation · CEREBRO |
| **Applied AI**: LLM agents, structured output, agentic workflows | CEREBRO · Second Brain |

---

## Table of Contents

- [MSc Dissertation](#msc-dissertation)
- [Academic Projects](#academic-projects)
- [Personal Projects](#personal-projects)
- [Repository Structure](#repository-structure)
- [License](#license)

---

## MSc Dissertation

### Dockerfile Refactorings: Detection and Effects

MSc dissertation at **ISEP**, supervised by Prof. Isabel Azevedo, following **Design Science Research**.

**The problem.** Refactoring is routine in application code but rare in infrastructure as code. In Dockerfiles, one refactoring can push performance, security and maintainability in opposite directions. For example, merging `RUN` instructions shrinks the image but makes the file harder to read. Developers refactor without knowing the real effect. Existing tools solve only half the problem: DRMiner detects refactorings but doesn't measure them, and Hadolint lints a single version of the file with no history.

**Contributions.**

- **Extended catalogue.** Takes the 14 refactorings of Ksontini et al. and rates each one on three independent dimensions (performance, security, maintainability) as an improvement, a degradation or neutral. The ratings are backed by the literature and by 15 controlled experiments.
- **Prototype.** A four-stage Python pipeline:
  1. Reads a Dockerfile at two commits without a checkout (GitPython).
  2. Detects the refactoring with 14 structural rules (dockerfile-parse).
  3. Builds both images and measures **ΔSize** (Docker SDK), **ΔCVEs** (Trivy), **ΔWarnings** (Hadolint) and **ΔInstr** (logical instructions).
  4. Writes a JSON report.

**Results.**

| Dimension | Result |
|---|---|
| Detection | 100% conformance over 49 commit pairs: no false positives, no false negatives |
| Performance | −24,812,684 bytes (≈ −24.8 MB) moving from `debian:12-slim` to `alpine:3.19` |
| Security | CRITICAL CVEs 56 → 2 · HIGH 1,894 → 21 |
| Maintainability | ΔWarnings −1 · ΔInstr −1 |

**Limitations.** The tool analyses one Dockerfile at a time, so refactorings that span several files (R11) are poorly measured. Image sizes drift by a few bytes between identical builds, and the author built the evaluation corpus.

**Demonstrates:** Design Science Research · PRISMA systematic literature review · static analysis over Git history · automated image building and vulnerability measurement · tested Python architecture (302 tests, 94% coverage)
**Tech:** Python · Docker SDK · Trivy · Hadolint · GitPython · dockerfile-parse · pytest
**Details:** [`msc-thesis/dockerfile-refactorings-detection-and-effects/`](./msc-thesis/dockerfile-refactorings-detection-and-effects/) · [dissertation PDF](./msc-thesis/dockerfile-refactorings-detection-and-effects/report/Dissertation_DiogoVieira_1240448.pdf)

---

## Academic Projects

Course projects from the MEng in Computer Engineering at ISEP.

### Empirical Evaluation of Security Scanners for Docker Containers

A comparative **empirical evaluation of four container vulnerability scanners**: **Trivy, Grype, Snyk and Docker Scout**. It uses the **Goal‑Question‑Metric (GQM)** methodology over ten Docker images with distinct risk profiles: clean baselines, EOSL systems, and images carrying Shellshock, SambaCry, Log4Shell, Spring4Shell and a Confluence RCE.

The study quantifies real scanner blind spots:
- a **0% detection rate for Shellshock across all four tools**, because software compiled from source is invisible to metadata scanning;
- Docker Scout reporting **zero CVEs on EOSL Debian** while finding 848 on Ubuntu 16.04;
- a **6.5× spread in vulnerability counts for the same image** (140 vs. 918).

It closes with use‑case recommendations and per‑tool performance (Trivy fastest at 4.39 s, Snyk slowest at 19.81 s).

**Demonstrates:** GQM empirical methodology · hands‑on Trivy/Grype/Snyk/Docker Scout · reproducible vulnerable environments with Docker and Vulhub · JSON parsing and metric analysis in Python
**Tech:** Docker · Trivy · Grype · Snyk · Docker Scout · Vulhub · Python
**Details:** [`academic/vulnerability-scanner-evaluation/`](./academic/vulnerability-scanner-evaluation/) · report included

---

### PKI with mutual TLS (OpenSSL · NGINX · Flask)

A full **Public Key Infrastructure** built from scratch. It has three parts:
- a self‑signed **Root CA**;
- a subordinate **Intermediate CA** that issues end‑entity certificates;
- an **NGINX** server enforcing **mutual TLS (mTLS)**, so only clients holding a valid certificate signed by the chain reach the backend **Flask** app.

The certificate lifecycle (issue, **revoke** with CRLs, renew, reissue) is fully scripted behind an interactive menu.

**Demonstrates:** two‑tier CA / trust‑chain design · X.509 and CRL management · mTLS client authentication · security automation in Bash/OpenSSL
**Tech:** Bash · OpenSSL · NGINX · Flask · X.509 · CRL · Linux
**Details:** [`academic/pki-mtls-openssl-nginx/`](./academic/pki-mtls-openssl-nginx/) · report included

---

### Caesar Cipher Toolkit (Python)

A command‑line cryptography toolkit that implements classic substitution ciphers and frequency analysis from scratch, with no crypto libraries. It includes a letter‑frequency histogram, the Caesar shift cipher, a scrambled‑alphabet cipher and a dual‑key even/odd file cipher.

**Demonstrates:** symmetric ciphers from first principles · frequency analysis · key generation and modular arithmetic
**Tech:** Python 3 (standard library only)
**Details:** [`academic/caesar-cipher/`](./academic/caesar-cipher/)

---

### Connect Four — 3D (Three.js)

A browser‑based **Connect Four** rendered in 3D with Three.js. It has a full game loop with gravity, turn switching and 4‑in‑a‑row win detection in every direction, set in a glTF scene with custom textures and HDR lighting.

**Demonstrates:** real‑time 3D scene setup · game logic cleanly separated from rendering · directional win‑detection algorithm
**Tech:** JavaScript (ES modules) · Three.js · glTF
**Details:** [`academic/connect-four-3d/`](./academic/connect-four-3d/)

---

## Personal Projects

Projects I built on my own initiative.

### CEREBRO — AI‑Driven Secure Installer

A natural‑language software installer for Windows. You type *"install Discord"* and an **LLM agent** maps it to the right package. A multi‑stage pipeline then **verifies the installer's source before anything runs**: registered‑domain and trusted‑CDN checks block unverified third‑party hosts. Finally, control goes back to you to configure the install yourself.

**Demonstrates:** LLM agent design with structured (JSON‑schema) output · supply‑chain trust verification (eTLD+1 domain checks) · human‑in‑the‑loop safety gates · Windows/winget automation
**Tech:** Python · tkinter · Anthropic Claude API · winget
**Details:** [`personal/cerebro-secure-installer/`](./personal/cerebro-secure-installer/)

---

### Second Brain — LLM‑Maintained Knowledge Base

A personal knowledge system where an AI agent (Claude Code) incrementally **compiles raw notes into a heavily interlinked, Wikipedia‑style Obsidian wiki**. It builds source, entity and concept pages with bi‑directional links, so the assistant answers from *your* accumulated knowledge instead of from scratch.

It has three layers: immutable raw sources, an AI‑managed wiki, and a `CLAUDE.md` schema. A strict verbatim‑ingestion rule and a `!lint` health‑check workflow keep the wiki consistent.

**Demonstrates:** designing an agentic compiler with a rule schema · knowledge‑graph / information architecture · prompt and workflow engineering for Claude Code · privacy‑conscious design (engine published, personal notes kept private)
**Tech:** Claude Code · Obsidian · Markdown
**Details:** [`personal/second-brain/`](./personal/second-brain/): engine, templates and a runnable example (real notes kept private)

---

## Repository Structure

```
My-Projects/
├── README.md                                  # this portfolio index
├── LICENSE · .gitignore · .gitattributes
│
├── msc-thesis/
│   └── dockerfile-refactorings-detection-and-effects/   # MSc dissertation: prototype, experiments, lit review (+ PDF)
│
├── academic/                                  # course projects (MEng, ISEP)
│   ├── vulnerability-scanner-evaluation/      # empirical scanner evaluation (+ report)
│   ├── pki-mtls-openssl-nginx/                # PKI + mutual TLS (+ report, scripts)
│   ├── caesar-cipher/                         # Python cipher toolkit
│   └── connect-four-3d/                       # Three.js 3D Connect Four
│
└── personal/                                  # own-initiative projects
    ├── cerebro-secure-installer/              # AI natural-language installer + supply-chain checks
    └── second-brain/                          # note-graph knowledge system (engine only)
```

## License

Released under the [MIT License](./LICENSE).
