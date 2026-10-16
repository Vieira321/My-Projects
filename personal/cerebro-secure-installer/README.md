# CEREBRO — AI‑Driven Secure Installer for Windows

A natural‑language software installer for Windows that combines an **LLM agent** with a **supply‑chain security pipeline**. You type *"install Discord"* (or *"I need a browser"*) in plain language; an AI maps it to the right package, and a multi‑stage agent **verifies the installer's source before anything runs** — then hands control back to you to configure the install yourself.

The design goal is deliberate: **automate the boring part (finding and vetting the package), keep the human in control of the risky part (running and configuring the installer).**

---

## How it works

The system has two components:

### 1. `cerebro.py` — AI front‑end (GUI)

A chat‑style desktop app (tkinter) that turns a natural‑language request into a concrete package:

- Sends the request to the **Anthropic Claude API** with a **structured JSON schema**, getting back `{ search_term, confidence, reasoning }`.
- **Confidence‑aware:** a specific request (*"Java from Oracle"*) returns a high‑confidence exact package ID; a generic request (*"a browser"*) returns a **low‑confidence, multi‑option term** so the installer shows a picker instead of the model guessing for you.
- Launches `win_secure_installer.py` in a new console with the chosen term and any flags (`--force`, target version).

### 2. `win_secure_installer.py` — agentic install pipeline

A dependency‑free (stdlib + `winget`) pipeline of cooperating agents:

| Stage | Agent | Responsibility |
|---|---|---|
| 1 | **Pesquisador** (Researcher) | Searches winget, parses candidates, lets the user pick the exact package |
| 2 | **Verificador** (Verifier) | **Security checks** (see below) before any install runs |
| 3 | **Dependências** | Detects/handles package dependencies |
| 4 | **Instalador** | Runs the *interactive* installer through security gates |

---

## The security model (the core of the project)

### Domain‑trust verification (supply‑chain check)

Before installing, the Verifier extracts the **registered domain (eTLD+1)** of both the publisher's **homepage** and the actual **installer URL**, then classifies the result:

| Outcome | Meaning | Action |
|---|---|---|
| **Domain match** | Installer is hosted on the publisher's own domain | ✅ Trusted |
| **Trusted CDN** | Different domain, but a known distribution host (GitHub, Microsoft, AWS CloudFront, `discordapp.net`, …) | ⚠️ Allowed, flagged in the report |
| **Microsoft Store** | Package comes from Microsoft's signed delivery pipeline | ✅ Trusted |
| **Suspicious domain** | Installer URL's domain is unknown and ≠ homepage | ⛔ **Blocked** (requires `--force`) |

This catches the classic **supply‑chain risk** where a package's metadata points an installer at an unexpected third‑party domain.

### Security gates before running anything

The installer evaluates gates in order:

- **G1** — verification failed and no `--force` → **blocks**
- **G2** — already on the latest/target version and no `--force` → **skips**
- **G3** — warnings present and no `--force` → **asks for explicit confirmation**
- **G4** — proceeds with `winget install`/`upgrade`

Crucially, the final step launches the **interactive** winget installer (a 30‑minute timeout gives you time to configure it), so the user keeps control of installation options — the tool never silently configures software on your behalf.

---

## Usage

```bash
# GUI (natural language)
pip install anthropic
setx ANTHROPIC_API_KEY "sk-ant-..."     # your key — never commit it
python cerebro.py

# CLI (direct, no AI/API key needed)
python win_secure_installer.py discord
python win_secure_installer.py python --app-version 3.11.9
python win_secure_installer.py discord vscode vlc spotify   # multiple at once
python win_secure_installer.py flstudio --force             # bypass gates (at your own risk)
```

| Flag | Effect |
|---|---|
| `--app-version <v>` | Install an exact version |
| `--force` | Skip security gates / reinstall even if up to date |
| `--help` | Show usage |

> The CLI installer needs only Python (standard library) and **winget** (Windows `App Installer`). Only the AI GUI front‑end needs the `anthropic` package and an API key. Some packages (drivers, VMs, FL Studio) require running as Administrator.

## ⚠️ Safety notice

This tool downloads and runs software installers and may request Administrator privileges. The domain‑trust check reduces — but does not eliminate — supply‑chain risk; `--force` bypasses it entirely. Review what you install. Use at your own risk.

## Skills demonstrated

- Designing an **LLM agent** with structured (JSON‑schema) output and confidence‑driven control flow
- **Prompt engineering** for reliable natural‑language → package‑ID mapping with a picker fallback
- **Supply‑chain security thinking**: eTLD+1 domain extraction, trusted‑CDN allowlisting, blocking unverified sources
- **Human‑in‑the‑loop** safety design and staged security gates
- Windows automation with `winget`, a clean multi‑agent architecture, and a zero‑dependency installer core
