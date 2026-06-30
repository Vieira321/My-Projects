#!/usr/bin/env python3
"""
cerebro.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agente de Instalação com IA — Interface Gráfica (tkinter)

Uso:
    python cerebro.py

Requisitos:
    pip install anthropic
    set ANTHROPIC_API_KEY=sk-ant-...
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import subprocess
import sys
import os
import json
import re

# ── Anthropic import (graceful fallback) ─────────────────────────────────────
try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__))
INSTALLER_SCRIPT = os.path.join(SCRIPT_DIR, 'win_secure_installer.py')

# ── Load .env file if present ─────────────────────────────────────────────────
_env_file = os.path.join(SCRIPT_DIR, '.env')
if os.path.isfile(_env_file):
    with open(_env_file, encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _, _v = _line.partition('=')
                os.environ.setdefault(_k.strip(), _v.strip())

# ── Colours ───────────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
CHAT_BG  = "#252526"
INPUT_BG = "#2d2d2d"
FG       = "#d4d4d4"
FG_USER  = "#9cdcfe"
FG_AI    = "#4ec9b0"
FG_OK    = "#6a9955"
FG_WARN  = "#dcdcaa"
FG_ERR   = "#f44747"
FG_DIM   = "#858585"
ACCENT   = "#007acc"
BTN_BG   = "#0e639c"
BTN_FG   = "#ffffff"
SEP      = "#3c3c3c"

# ── Claude system prompt ───────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a Windows software expert specializing in winget package IDs.
Given a natural language install request, identify the best winget search term.

Respond ONLY with valid JSON (no markdown, no extra text):
{"search_term": "...", "confidence": "high" or "low", "reasoning": "..."}

Rules:
- If the user mentions a SPECIFIC variant, brand, or source (e.g. "java da oracle", "jre do java.com", "chrome do google") → return the exact winget ID (high confidence)
- If the user asks GENERICALLY (e.g. "instala o java", "quero um browser", "preciso de office") → return a SHORT generic search term (low confidence) so the user sees ALL available options
- NEVER invent winget IDs you are not sure exist
- When in doubt, prefer low confidence + generic term over guessing a specific ID

Common confirmed mappings (use ONLY when user is specific):
Java da Oracle / JRE / java.com      → Oracle.JavaRuntimeEnvironment
java (generic)                       → java  [low confidence — show all variants]
VS Code (specific)                   → Microsoft.VisualStudioCode
Discord (specific)                   → Discord.Discord
VLC (specific)                       → VideoLAN.VLC
Chrome / Google Chrome (specific)    → Google.Chrome
Firefox (specific)                   → Mozilla.Firefox
7-Zip (specific)                     → 7zip.7zip
Notepad++ (specific)                 → Notepad++.Notepad++
Steam (specific)                     → Valve.Steam
Spotify (specific)                   → Spotify.Spotify
Git (specific)                       → Git.Git
Node.js / Node / npm (specific)      → OpenJS.NodeJS
Python (generic)                     → python  [low confidence]
Zoom (specific)                      → Zoom.Zoom
Teams / Microsoft Teams (specific)   → Microsoft.Teams
OBS / OBS Studio (specific)          → OBSProject.OBSStudio

IMPORTANT — winget has NO category search. A single generic term like "browser" returns wrong obscure apps.
For CATEGORY requests, return pipe-separated specific IDs so the installer searches each one and merges results:

Category mappings (always low confidence, pipe-separated):
browser / navegador / internet     → "Google.Chrome|Mozilla.Firefox|Brave.Brave|Opera.Opera|Vivaldi.Vivaldi"
java jdk / jdk / java developer    → "Oracle.JDK.21|Microsoft.OpenJDK.21|Amazon.Corretto.21|Eclipse.Temurin.21"
java / jre / java runtime          → "Oracle.JavaRuntimeEnvironment|Microsoft.OpenJDK.21|Amazon.Corretto.21|Eclipse.Temurin.21"
office / escritório / word/excel   → "Microsoft.Office|LibreOffice.LibreOffice|OnlyOffice.DesktopEditors"
music player / leitor música       → "VideoLAN.VLC|AIMP.AIMP|foobar2000.foobar2000|MusicBee.MusicBee"
video editor / edição vídeo        → "DaVinciResolve.DaVinciResolve|OpenShot.OpenShot|Kdenlive.Kdenlive"
text editor / editor de texto      → "Notepad++.Notepad++|Microsoft.VisualStudioCode|Sublime.SublimeText"
torrent                            → "qBittorrent.qBittorrent|Deluge.Deluge|WeTorrent.WeeTorrent"
antivirus                          → "Malwarebytes.Malwarebytes|ESET.NOD32Antivirus"
pdf reader / leitor pdf            → "Adobe.Acrobat.Reader.64-bit|Foxit.FoxitReader|SumatraPDF.SumatraPDF"
compression / zip / compressão     → "7zip.7zip|RARLab.WinRAR|Giorgiotani.Peazip"
password manager                   → "Bitwarden.Bitwarden|KeePassXCTeam.KeePassXC|1Password.1Password"
communication / chat / social / rede social → "Discord.Discord|SlackTechnologies.Slack|Microsoft.Teams|Telegram.TelegramDesktop|OpenWhisperSystems.Signal"
screen recorder / gravação         → "OBSProject.OBSStudio|Greenshot.Greenshot|ShareX.ShareX"

Examples:
"instala o java" → {"search_term": "java", "confidence": "low", "reasoning": "Genérico"}
"instala o java da oracle" → {"search_term": "Oracle.JavaRuntimeEnvironment", "confidence": "high", "reasoning": "Específico"}
"preciso de um browser" → {"search_term": "Google.Chrome|Mozilla.Firefox|Brave.Brave|Opera.Opera|Vivaldi.Vivaldi", "confidence": "low", "reasoning": "Categoria browser — a mostrar todas as opções principais"}
"instala o VS Code" → {"search_term": "Microsoft.VisualStudioCode", "confidence": "high", "reasoning": "Específico"}
Audacity                             → Audacity.Audacity
PowerShell                           → Microsoft.PowerShell
WinRAR                               → RARLab.WinRAR
Everything (search)                  → voidtools.Everything
qBittorrent                          → qBittorrent.qBittorrent
VirtualBox                           → Oracle.VirtualBox
PuTTY                                → PuTTY.PuTTY"""


class CerebroApp(tk.Tk):
    """Chat-style GUI that translates natural language → winget installs."""

    def __init__(self):
        super().__init__()
        self._client   = None
        self._thinking = None   # mark of the "A pensar…" line index
        self._busy     = False

        self._setup_window()
        self._setup_ui()
        self._welcome()
        self._check_prerequisites()

    # ── Window ────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.title("🧠 CEREBRO — Instalador com IA")
        self.geometry("720x580")
        self.minsize(560, 420)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Centre on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 720) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"+{x}+{y}")

    # ── UI layout ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        mono10 = ("Consolas", 10)
        mono11 = ("Consolas", 11)

        # ── Header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=ACCENT, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="🧠  CEREBRO — Instalador com IA",
            bg=ACCENT, fg="#ffffff",
            font=("Consolas", 12, "bold"), anchor="w", padx=12
        ).pack(side="left", fill="y")

        # ── Chat area ─────────────────────────────────────────────────────────
        chat_frame = tk.Frame(self, bg=CHAT_BG)
        chat_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._chat = tk.Text(
            chat_frame,
            bg=CHAT_BG, fg=FG,
            font=mono10,
            state="disabled",
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=14, pady=10,
            spacing1=2, spacing3=4,
            cursor="arrow",
        )
        sb = tk.Scrollbar(chat_frame, command=self._chat.yview, bg=BG,
                          troughcolor=BG, relief="flat", width=10)
        self._chat.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._chat.pack(side="left", fill="both", expand=True)

        # Text tags
        self._chat.tag_configure("user",   foreground=FG_USER,
                                 font=("Consolas", 10, "bold"))
        self._chat.tag_configure("ai",     foreground=FG_AI,
                                 font=mono10)
        self._chat.tag_configure("ok",     foreground=FG_OK,  font=mono10)
        self._chat.tag_configure("warn",   foreground=FG_WARN, font=mono10)
        self._chat.tag_configure("err",    foreground=FG_ERR,  font=mono10)
        self._chat.tag_configure("dim",    foreground=FG_DIM,
                                 font=("Consolas", 9, "italic"))
        self._chat.tag_configure("header", foreground=ACCENT,
                                 font=("Consolas", 10, "bold"))
        self._chat.tag_configure("code",   foreground="#ce9178", font=mono10)
        self._chat.tag_configure("sep",    foreground=SEP, font=("Consolas", 6))

        # ── Options bar (force + version) ─────────────────────────────────────
        opt = tk.Frame(self, bg=INPUT_BG, pady=6, padx=12)
        opt.pack(fill="x")

        self._force_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt, text="  --force", variable=self._force_var,
            bg=INPUT_BG, fg=FG_WARN, selectcolor=BG,
            activebackground=INPUT_BG, activeforeground=FG_WARN,
            font=mono10, relief="flat", cursor="hand2",
        ).pack(side="left")

        tk.Label(opt, text="  Versão:", bg=INPUT_BG, fg=FG_DIM,
                 font=mono10).pack(side="left")
        self._ver_entry = tk.Entry(
            opt, bg=BG, fg=FG, insertbackground=FG,
            font=mono10, relief="flat", width=14, bd=0,
        )
        self._ver_entry.pack(side="left", padx=(4, 0), ipady=3)

        # divider
        tk.Frame(self, bg=SEP, height=1).pack(fill="x")

        # ── Input bar ─────────────────────────────────────────────────────────
        inp = tk.Frame(self, bg=INPUT_BG, pady=8, padx=10)
        inp.pack(fill="x")

        self._entry = tk.Entry(
            inp, bg=BG, fg=FG, insertbackground=FG,
            font=mono11, relief="flat", bd=0,
        )
        self._entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(2, 8))
        self._entry.bind("<Return>", self._on_send)

        self._btn = tk.Button(
            inp, text="  ▶  Instalar  ", command=self._on_send,
            bg=BTN_BG, fg=BTN_FG, activebackground="#1177bb",
            activeforeground=BTN_FG, font=("Consolas", 10, "bold"),
            relief="flat", bd=0, cursor="hand2", padx=6, pady=4,
        )
        self._btn.pack(side="right")

        # placeholder logic
        self._entry.insert(0, "O que queres instalar?")
        self._entry.config(fg=FG_DIM)
        self._entry.bind("<FocusIn>",  self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.focus_set()

    # ── Placeholder helpers ───────────────────────────────────────────────────

    def _on_focus_in(self, _=None):
        if self._entry.get() == "O que queres instalar?":
            self._entry.delete(0, "end")
            self._entry.config(fg=FG)

    def _on_focus_out(self, _=None):
        if not self._entry.get().strip():
            self._entry.insert(0, "O que queres instalar?")
            self._entry.config(fg=FG_DIM)

    # ── Chat helpers ──────────────────────────────────────────────────────────

    def _add(self, text: str, tag: str = "", newline: bool = True):
        """Append text to chat widget (thread-safe via after)."""
        def _insert():
            self._chat.config(state="normal")
            self._chat.insert("end", text + ("\n" if newline else ""), tag)
            self._chat.see("end")
            self._chat.config(state="disabled")
        self.after(0, _insert)

    def _add_sep(self):
        self._add("─" * 62, "sep")

    def _remove_thinking(self):
        """Delete the 'A pensar…' line."""
        def _del():
            self._chat.config(state="normal")
            # find and remove last dim line
            idx = self._chat.search("A pensar", "1.0", "end")
            if idx:
                line_start = f"{idx.split('.')[0]}.0"
                line_end   = f"{idx.split('.')[0]}.end+1c"
                self._chat.delete(line_start, line_end)
            self._chat.config(state="disabled")
        self.after(0, _del)

    # ── Welcome & prerequisites ────────────────────────────────────────────────

    def _welcome(self):
        self._add("━" * 62, "sep")
        self._add("  🧠  CEREBRO — Instalador com IA", "header")
        self._add("  Diz-me o que queres instalar em linguagem natural.", "dim")
        self._add("  Ex: \"Instala o Java do site oficial\"", "dim")
        self._add("      \"quero o discord\"", "dim")
        self._add("      \"preciso do python 3.11\"", "dim")
        self._add("━" * 62, "sep")
        self._add("")

    def _check_prerequisites(self):
        if not ANTHROPIC_OK:
            self._add("⚠  Biblioteca 'anthropic' não instalada.", "warn")
            self._add("   Corre:  pip install anthropic", "code")
            self._add("")
            return

        if not os.environ.get("ANTHROPIC_API_KEY"):
            self._add("⚠  ANTHROPIC_API_KEY não configurada.", "warn")
            self._add("   Define a variável de ambiente antes de iniciar:", "dim")
            self._add("   set ANTHROPIC_API_KEY=sk-ant-...", "code")
            self._add("")
            return

        if not os.path.isfile(INSTALLER_SCRIPT):
            self._add("✖  win_secure_installer.py não encontrado em:", "err")
            self._add(f"   {INSTALLER_SCRIPT}", "code")
            self._add("")
            return

        self._client = anthropic.Anthropic()
        self._add("✔  Pronto. Winget e API ligados.", "ok")
        self._add("")

    # ── Send handler ─────────────────────────────────────────────────────────

    def _on_send(self, _=None):
        if self._busy:
            return

        phrase = self._entry.get().strip()
        if not phrase or phrase == "O que queres instalar?":
            return

        # Clear input
        self._entry.delete(0, "end")
        self._on_focus_out()

        if not self._client:
            self._add("✖  API não disponível. Verifica os requisitos acima.", "err")
            return

        self._busy = True
        self._btn.config(state="disabled", bg="#555555")
        self._entry.config(state="disabled")

        self._add(f"  Tu:  {phrase}", "user")
        self._add("")

        threading.Thread(target=self._process, args=(phrase,), daemon=True).start()

    # ── Processing pipeline ───────────────────────────────────────────────────

    def _process(self, phrase: str):
        self._add("  🧠 IA:  A pensar…", "dim")

        try:
            result = self._call_ai(phrase)
        except Exception as exc:
            self._remove_thinking()
            self._add(f"  ✖  Erro ao contactar IA: {exc}", "err")
            self._add("")
            self._set_idle()
            return

        self._remove_thinking()

        search_term = result.get("search_term", "").strip()
        confidence  = result.get("confidence", "low")
        reasoning   = result.get("reasoning", "")

        if not search_term:
            self._add("  ✖  IA não conseguiu identificar a aplicação.", "err")
            self._add("     Tenta ser mais específico.", "dim")
            self._add("")
            self._set_idle()
            return

        # Show AI decision
        conf_icon = "✔" if confidence == "high" else "⚠"
        conf_tag  = "ok"  if confidence == "high" else "warn"
        conf_text = "alta confiança" if confidence == "high" else "baixa confiança — picker vai aparecer"

        self._add(f"  🧠 IA:", "ai", newline=False)
        self._add(f"  {conf_icon}  {search_term}", conf_tag)
        self._add(f"       {reasoning}", "dim")
        self._add(f"       Confiança: {conf_text}", conf_tag)
        self._add("")

        # Collect flags
        force   = self._force_var.get()
        version = self._ver_entry.get().strip()

        self._add("  ℹ  A lançar win_secure_installer.py…", "dim")
        self._launch(search_term, force, version)

    def _call_ai(self, phrase: str) -> dict:
        """Call Claude API and return parsed JSON result."""
        response = self._client.messages.create(
            model="claude-opus-4-6",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "search_term": {"type": "string"},
                            "confidence":  {"type": "string",
                                           "enum": ["high", "low"]},
                            "reasoning":   {"type": "string"},
                        },
                        "required": ["search_term", "confidence", "reasoning"],
                        "additionalProperties": False,
                    }
                }
            },
            messages=[{"role": "user", "content": phrase}],
        )
        text = next((b.text for b in response.content if b.type == "text"), "{}")
        # Strip markdown fences if present
        text = re.sub(r"^```[a-z]*\n?", "", text.strip())
        text = re.sub(r"\n?```$",       "", text.strip())
        return json.loads(text)

    def _launch(self, search_term: str, force: bool, version: str):
        """Open a new terminal window running win_secure_installer.py."""
        cmd = [sys.executable, '-X', 'utf8', INSTALLER_SCRIPT, search_term]
        if force:
            cmd.append("--force")
        if version:
            cmd += ["--app-version", version]

        try:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            self._add("  ✔  Terminal aberto — conclua a instalação"
                      " na janela que apareceu.", "ok")
        except Exception as exc:
            self._add(f"  ✖  Falha ao lançar instalador: {exc}", "err")

        self._add_sep()
        self._add("")
        self._set_idle()

    def _set_idle(self):
        def _unlock():
            self._busy = False
            self._btn.config(state="normal", bg=BTN_BG)
            self._entry.config(state="normal")
            self._entry.focus_set()
        self.after(0, _unlock)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = CerebroApp()
    app.mainloop()


if __name__ == "__main__":
    main()
