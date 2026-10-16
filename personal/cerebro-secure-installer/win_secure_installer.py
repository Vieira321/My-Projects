#!/usr/bin/env python3
"""
win_secure_installer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sistema de Instalação Agêntica para Windows  |  3-Stage Pipeline
  Agente_Pesquisador  →  Agente_Verificador  →  Agente_Instalador_Silent

Uso:
    python win_secure_installer.py <app> [--app-version <versão>] [--force]
    python win_secure_installer.py <app1> [app2 ...] [--force]

Exemplos:
    python win_secure_installer.py python --app-version 3.11.9
    python win_secure_installer.py discord
    python win_secure_installer.py discord vscode vlc spotify
    python win_secure_installer.py flstudio --force

Flags:
    --app-version <v>  Instala a versão exacta especificada (ex: 3.11.9)
    --force            Ignora erros de segurança e reinstala se já atualizado
    --help             Mostra esta ajuda

Dependências: apenas stdlib (subprocess, sys, re, json, ctypes, urllib.parse)
"""

import subprocess
import sys
import re
import ctypes
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Force UTF-8 output so box-drawing characters work on all Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# ══════════════════════════════════════════════════════════════════════════════
# ANSI COLORS & TERMINAL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

class C:
    """ANSI escape codes for terminal coloring."""
    RST  = '\033[0m'
    BOLD = '\033[1m'
    DIM  = '\033[2m'
    RED  = '\033[91m'
    GRN  = '\033[92m'
    YLW  = '\033[93m'
    BLU  = '\033[94m'
    CYN  = '\033[96m'


def enable_ansi() -> None:
    """Activate ANSI escape code processing on Windows 10/11 terminals."""
    import os
    os.system('')   # VT processing is enabled as a side-effect of any system() call


def _strip_ansi(text: str) -> str:
    """Return text with all ANSI escape sequences removed (for length math)."""
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _is_msstore_id(app_id: str) -> bool:
    """
    Return True if the App ID follows the Microsoft Store format.

    Store IDs are uppercase alphanumeric strings of 9–20 characters with no dots
    (e.g. '9NBLGGH4NNS1', 'XPFFTQ037JWMHS').  winget IDs always contain at least
    one dot (e.g. 'Discord.Discord', 'Microsoft.VisualStudioCode').
    """
    return bool(re.match(r'^[A-Z0-9]{9,20}$', app_id))


# ── Line printers ─────────────────────────────────────────────────────────────

def pok(msg: str, detail: str = '') -> None:
    print(f"  {C.GRN}✔{C.RST} {msg} {C.DIM}{detail}{C.RST}")

def pwarn(msg: str, detail: str = '') -> None:
    print(f"  {C.YLW}⚠{C.RST} {C.YLW}{msg}{C.RST} {C.DIM}{detail}{C.RST}")

def perr(msg: str, detail: str = '') -> None:
    print(f"  {C.RED}✖{C.RST} {C.RED}{msg}{C.RST} {C.DIM}{detail}{C.RST}")

def pinfo(msg: str, detail: str = '') -> None:
    print(f"  {C.CYN}ℹ{C.RST} {msg} {C.DIM}{detail}{C.RST}")

def psection(title: str) -> None:
    print(f"\n{C.BOLD}{C.BLU}▶ {title}{C.RST}")

def pheader(title: str) -> None:
    W = 64
    bar = '═' * W
    padded = f"  {title}"
    print(f"\n{C.BOLD}{C.CYN}╔{bar}╗")
    print(f"║{C.RST}{C.BOLD}{padded:<{W}}{C.CYN}║")
    print(f"╚{bar}╝{C.RST}")


# ══════════════════════════════════════════════════════════════════════════════
# CORE UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def is_admin() -> bool:
    """Return True if the current process has Administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except AttributeError:
        return False


def check_winget() -> bool:
    """Verify winget is available in PATH."""
    rc, _, _ = _run(['winget', '--version'])
    return rc == 0


def _run(cmd: List[str], timeout: int = 90) -> tuple:
    """
    Run a subprocess command silently.
    Returns (returncode: int, stdout: str, stderr: str).
    """
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return -1, '', f"Comando não encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -1, '', f"Timeout a executar: {' '.join(cmd)}"


# ── Domain Trust Logic ────────────────────────────────────────────────────────

def get_registered_domain(url: str) -> str:
    """
    Extract the registered domain (eTLD+1) from a URL — without external libs.

    Algorithm:
      1. Parse netloc via urllib.parse (handles scheme, port, path correctly).
      2. Strip leading 'www.' prefix.
      3. Check against a hard-coded set of known multi-part TLDs
         (co.uk, com.br, …). If the last two labels form one of these,
         include the third-to-last label as well.
      4. Otherwise return the last two dot-separated labels.

    Examples:
      https://dl.discordapp.net/setup.exe  →  discordapp.net
      https://discord.com/download         →  discord.com
      https://github.com/user/repo         →  github.com
      https://objects.githubusercontent.com →  githubusercontent.com
      https://store.epicgames.com          →  epicgames.com
    """
    if not url:
        return ''
    try:
        parsed = urlparse(url.strip())
        netloc = (parsed.netloc or parsed.path).lower()
        netloc = netloc.split(':')[0]           # strip port
        netloc = re.sub(r'^www\.', '', netloc)  # strip www
        parts  = netloc.split('.')

        MULTI_TLDS = {
            'co.uk', 'org.uk', 'me.uk', 'net.uk', 'ltd.uk', 'plc.uk',
            'com.br', 'org.br', 'net.br', 'edu.br',
            'com.au', 'net.au', 'org.au', 'edu.au',
            'co.jp',  'ne.jp',  'or.jp',
            'co.nz',  'org.nz', 'net.nz',
            'com.ar', 'com.mx', 'com.sg', 'com.hk',
        }
        if len(parts) >= 3 and '.'.join(parts[-2:]) in MULTI_TLDS:
            return '.'.join(parts[-3:])
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return netloc
    except Exception:
        return ''


# Domains considered trustworthy as distribution / CDN hosts even when they
# differ from the publisher's own homepage domain.
TRUSTED_CDN_HOSTS: frozenset = frozenset({
    # Source-code / release hosting
    'github.com', 'githubusercontent.com', 'objects.githubusercontent.com',
    # Microsoft CDN & delivery
    'microsoft.com', 'windows.net', 'azureedge.net', 'azurefd.net',
    'dl.delivery.mp.microsoft.com', 'download.microsoft.com',
    # Cloud object storage
    'amazonaws.com', 'cloudfront.net', 'fastly.net',
    'akamaiedge.net', 'akamaihd.net',
    # Well-known publisher CDN subdomains (registered domain ≠ homepage domain)
    'discordapp.net',    # Discord uses discord.com as homepage
    'slack-edge.com',    # Slack uses slack.com as homepage
    'zoom.us',           # Zoom distribution domain
    'epicgames.com',     # Epic Games launcher
    'steamcdn-a.akamaihd.net',
})


def is_trusted_cdn(installer_url: str) -> bool:
    """Return True if the installer URL's host is a known CDN / distribution endpoint."""
    netloc = urlparse(installer_url).netloc.lower()
    return any(cdn in netloc for cdn in TRUSTED_CDN_HOSTS)


# ══════════════════════════════════════════════════════════════════════════════
# AGENTE 1 — PESQUISADOR  (ID & Metadata)
# ══════════════════════════════════════════════════════════════════════════════

def agente_pesquisador(app_name: str,
                       target_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Localiza o App ID oficial no winget e extrai Publisher, Homepage,
    Installer URL, versão disponível, SHA-256 e fonte (winget / msstore).

    Fluxo:
      1. _search_and_select()  → escolhe o melhor candidato,
                                  pedindo confirmação se houver ambiguidade
      2. winget show --id <ID> → detalhes completos
    """
    psection(f"[PESQUISADOR] Identificando: '{app_name}'")

    # Step 1 — Search & Disambiguate ─────────────────────────────────────────
    selected = _search_and_select(app_name)
    if not selected:
        return None

    app_id = selected['id']
    source = selected['source']   # 'winget' | 'msstore'

    src_label = f"{C.BLU}Microsoft Store{C.RST}" if source == 'msstore' \
                else f"{C.CYN}winget — Web{C.RST}"
    pok(f"ID encontrado [{src_label}{C.RST}]:", app_id)

    # Step 2 — Get Full Metadata ──────────────────────────────────────────────
    rc, stdout, stderr = _run(['winget', 'show', '--id', app_id,
                               '--accept-source-agreements'])
    if rc != 0:
        perr("Falha ao obter detalhes", stderr[:120])
        return None

    metadata = _parse_show_output(stdout)
    metadata['id']             = app_id
    metadata['name']           = selected.get('name', '')
    metadata['query']          = app_name
    metadata['source']         = source
    metadata['target_version'] = target_version

    # ── Confirmação do utilizador (mesmo estilo do picker) ────────────────────
    src_tag = f"{C.BLU}[Store]{C.RST}" if source == 'msstore' \
              else f"{C.CYN}[Web  ]{C.RST}"
    print()
    print(f"  {C.YLW}{'─'*56}{C.RST}")
    print(f"  {C.BOLD}Confirmas a instalação?{C.RST}")
    print()
    print(f"    {src_tag} {C.BOLD}{app_id}{C.RST}")
    if metadata.get('name'):
        print(f"         {C.DIM}Nome:      {metadata['name']}{C.RST}")
    if metadata.get('publisher'):
        print(f"         {C.DIM}Publisher: {metadata['publisher']}{C.RST}")
    if metadata.get('version'):
        print(f"         {C.DIM}Versão:    {metadata['version']}{C.RST}")
    if target_version:
        print(f"         {C.DIM}Versão alvo: {C.YLW}{target_version}{C.RST}")
    homepage = metadata.get('homepage', '')
    if homepage:
        print(f"         {C.DIM}Site:      {C.BLU}{homepage}{C.RST}")
    if source == 'msstore':
        print(f"         {C.DIM}Installer: Microsoft Store{C.RST}")
    else:
        installer_url = metadata.get('installer_url', '')
        if installer_url:
            short = (installer_url[:60] + '…') if len(installer_url) > 61 else installer_url
            print(f"         {C.DIM}Installer: {short}{C.RST}")
    print()
    print(f"  {C.YLW}{'─'*56}{C.RST}")
    try:
        answer = input(f"  {C.BOLD}[s/n]{C.RST} › ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = 'n'
    if answer not in ('s', 'sim', 'y', 'yes'):
        pwarn("Instalação cancelada pelo utilizador.")
        return None
    print()

    return metadata


def _parse_search_results(output: str, app_name: str) -> List[Dict[str, Any]]:
    """
    Converte a tabela de `winget search` numa lista de candidatos com score.

    Cada candidato é um dict: {name, id, source, score}.

    Scoring:
      +10  nome exacto              +6  nome começa com o termo
      +4   nome contém o termo      +3  ID contém o termo
      +2   formato Publisher.App    +1  fonte é winget (preferir sobre Store)

    A coluna 'Source' é extraída directamente do cabeçalho da tabela;
    como fallback, IDs sem ponto que sejam 9-20 chars maiúsculos são
    classificados como 'msstore' via _is_msstore_id().
    """
    lines     = output.strip().splitlines()
    app_lower = app_name.lower()

    # Locate header row
    header_idx = id_col = source_col = -1
    for i, line in enumerate(lines):
        if re.search(r'\bId\b', line) and re.search(r'\bName\b', line):
            header_idx = i
            m = re.search(r'\bId\b', line)
            id_col = m.start() if m else -1
            m2 = re.search(r'\bSource\b', line, re.IGNORECASE)
            source_col = m2.start() if m2 else -1
            break

    if header_idx == -1 or id_col == -1:
        return []

    candidates: List[Dict[str, Any]] = []
    for line in lines[header_idx + 2:]:   # skip separator
        if not line.strip() or len(line) <= id_col:
            continue
        m = re.match(r'(\S+)', line[id_col:])
        if not m:
            continue
        app_id = m.group(1)
        name   = line[:id_col].strip()

        # Detect source from column, then fallback to ID pattern
        source = 'winget'
        if source_col > 0 and len(line) > source_col:
            src_m = re.match(r'(\S+)', line[source_col:])
            if src_m:
                source = src_m.group(1).lower()
        if source not in ('winget', 'msstore'):
            source = 'msstore' if _is_msstore_id(app_id) else 'winget'

        name_lower = name.lower()
        score = 0
        if app_lower == name_lower:               score += 10
        elif name_lower.startswith(app_lower):    score += 6
        elif app_lower in name_lower:             score += 4
        if app_lower in app_id.lower():           score += 3
        if app_id.count('.') == 1:                score += 2
        if source == 'winget':                    score += 1

        candidates.append({'name': name, 'id': app_id,
                           'source': source, 'score': score})

    candidates.sort(key=lambda x: (-x['score'], len(x['id'])))
    return candidates


def _fetch_quick_meta(app_id: str) -> Dict[str, str]:
    """Fetch homepage and version for a single winget ID (used in parallel)."""
    try:
        rc, stdout, _ = _run(['winget', 'show', '--id', app_id,
                               '--accept-source-agreements'], timeout=12)
        if rc != 0:
            return {}
        meta = _parse_show_output(stdout)
        return {
            'homepage': meta.get('homepage', ''),
            'version':  meta.get('version', ''),
        }
    except Exception:
        return {}


def _show_candidates(candidates: List[Dict[str, Any]],
                     app_name: str) -> Optional[Dict[str, Any]]:
    """
    Mostra SEMPRE a lista de resultados com detalhes completos (Nome, Versão, Site),
    independentemente de ser 1 ou múltiplos resultados.
    Para 1 resultado: mostra e pede Enter para confirmar ou 0 para cancelar.
    Para múltiplos: pede escolha [1-N] ou 0 para cancelar.
    """
    shown = candidates[:15]

    # Fetch details for all in parallel
    print(f"\n  {C.DIM}A obter detalhes dos candidatos…{C.RST}", flush=True)
    details: Dict[str, Dict[str, str]] = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(_fetch_quick_meta, c['id']): c['id'] for c in shown}
        for fut in as_completed(futures):
            details[futures[fut]] = fut.result()

    print()
    label = f"1 resultado encontrado para '{app_name}':" if len(shown) == 1 \
            else f"{len(shown)} resultados para '{app_name}' — escolhe a aplicação:"
    pwarn(label)
    print()

    for i, c in enumerate(shown, 1):
        src_tag  = f"{C.BLU}[Store]{C.RST}" if c['source'] == 'msstore' \
                   else f"{C.CYN}[Web  ]{C.RST}"
        meta     = details.get(c['id'], {})
        version  = meta.get('version', '')
        homepage = meta.get('homepage', '')
        print(f"    {C.BOLD}[{i:>2}]{C.RST} {src_tag} {C.BOLD}{c['id']}{C.RST}")
        print(f"         {C.DIM}Nome:    {c['name']}{C.RST}")
        if version:
            print(f"         {C.DIM}Versão:  {version}{C.RST}")
        if homepage:
            print(f"         {C.DIM}Site:    {C.BLU}{homepage}{C.RST}")
        print()

    if len(shown) == 1:
        print(f"  {C.BOLD}Prima Enter para continuar ou 0 para cancelar:{C.RST} ",
              end='', flush=True)
        try:
            resp = input().strip()
        except (EOFError, KeyboardInterrupt):
            resp = '0'
        if resp == '0':
            perr("Seleção cancelada")
            return None
        return shown[0]
    else:
        print(f"  {C.BOLD}Escolha [1-{len(shown)}] ou 0 para cancelar:{C.RST} ",
              end='', flush=True)
        try:
            resp = input().strip()
        except (EOFError, KeyboardInterrupt):
            resp = '0'
        if not resp.isdigit() or resp == '0':
            perr("Seleção cancelada")
            return None
        idx = int(resp) - 1
        if 0 <= idx < len(shown):
            return shown[idx]
        perr("Opção inválida")
        return None


def _search_and_select(app_name: str) -> Optional[Dict[str, Any]]:
    """Pesquisa no winget e mostra sempre todos os resultados com detalhes.
    Suporta múltiplos termos separados por '|' (ex: categorias como browsers)."""

    terms = [t.strip() for t in app_name.split('|') if t.strip()]

    if len(terms) > 1:
        # Category search: run one search per term and merge unique results
        all_candidates: List[Dict[str, Any]] = []
        seen_ids: set = set()
        for term in terms:
            rc, stdout, _ = _run(['winget', 'search', '--id', term, '--exact',
                                   '--accept-source-agreements'])
            if rc == 0 and stdout.strip():
                for c in _parse_search_results(stdout, term):
                    if c['id'] not in seen_ids:
                        seen_ids.add(c['id'])
                        all_candidates.append(c)
        if not all_candidates:
            perr(f"Nenhum resultado encontrado para a categoria '{app_name}'")
            return None
        return _show_candidates(all_candidates, "categoria")

    # Single term search
    rc, stdout, _ = _run(['winget', 'search', app_name,
                          '--accept-source-agreements'])
    if rc != 0 or not stdout.strip():
        perr(f"Nenhum resultado encontrado para '{app_name}'")
        return None

    candidates = _parse_search_results(stdout, app_name)
    if not candidates:
        perr(f"Não foi possível identificar '{app_name}' nos resultados")
        return None

    return _show_candidates(candidates, app_name)


def _parse_show_output(output: str) -> Dict[str, Any]:
    """
    Transforma a saída de texto de `winget show` num dicionário estruturado.

    Campos extraídos (case-insensitive, first-match):
      Version / Publisher / Homepage / Publisher Url
      Download Url / Installer Url / InstallerUrl
      SHA256 / InstallerSha256
    """
    meta: Dict[str, Any] = {
        'version': '', 'publisher': '',
        'homepage': '', 'installer_url': '', 'sha256': '',
        'source': '',   # populated by agente_pesquisador after search
        'dependencies': [],
    }

    # Ordered list: (regex_pattern, target_key)
    FIELDS = [
        (r'^\s*Version\s*:',                     'version'),
        (r'^\s*Publisher\s*:',                   'publisher'),
        (r'^\s*Homepage\s*:',                    'homepage'),
        (r'^\s*Publisher\s+Url\s*:',             'homepage'),       # fallback
        (r'^\s*(Download|Installer)\s+Url\s*:',  'installer_url'),
        (r'^\s*InstallerUrl\s*:',                'installer_url'),
        (r'^\s*(Installer)?SHA256\s*:',          'sha256'),
        (r'^\s*InstallerSha256\s*:',             'sha256'),
    ]

    in_deps = False
    in_pkg_deps = False

    for line in output.splitlines():
        # ── Dependency parsing ────────────────────────────────────────────────
        stripped = line.strip()
        indent   = len(line) - len(line.lstrip())

        if re.match(r'^Dependencies\s*:', stripped, re.IGNORECASE):
            in_deps = True
            in_pkg_deps = False
            continue
        if in_deps:
            if indent == 0 and stripped:          # new top-level section
                in_deps = in_pkg_deps = False
            elif re.match(r'^Package\s*:', stripped, re.IGNORECASE):
                in_pkg_deps = True
                continue
            elif re.match(r'^\w[^:]*:', stripped): # other sub-section
                in_pkg_deps = False
                continue
            elif in_pkg_deps and stripped:
                dep_id = stripped.split()[0]       # strip ">= x.x" constraints
                if dep_id:
                    meta['dependencies'].append(dep_id)
            continue

        # ── Field parsing ─────────────────────────────────────────────────────
        for pattern, field in FIELDS:
            if re.match(pattern, line, re.IGNORECASE):
                value = line.split(':', 1)[1].strip()
                if not value:
                    break
                if field == 'publisher' and value.startswith('http'):
                    break
                if field in ('installer_url', 'homepage') and meta[field]:
                    break
                meta[field] = value
                break

    return meta


# ══════════════════════════════════════════════════════════════════════════════
# AGENTE 2 — VERIFICADOR  (Security & Version Match)
# ══════════════════════════════════════════════════════════════════════════════

def agente_verificador(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Realiza duas verificações de segurança/compatibilidade antes de instalar.

    ── Verificação 1 — Domain Trust ──────────────────────────────────────────
    Compara o domínio registado (eTLD+1) da Homepage com o do Installer URL.

      • MATCH  → mesmo domínio registado → TRUSTED ✔
      • CDN    → domínio diferente mas presente na TRUSTED_CDN_HOSTS → WARNING
                 (permite instalação automática, mas avisa no relatório)
      • ALERT  → domínio desconhecido / suspeito → BLOQUEADO
                 (requer --force ou confirmação manual)

    ── Verificação 2 — Version Check ─────────────────────────────────────────
    Executa `winget list --id <ID>` e compara a versão instalada com a
    disponível. Classifica como: novo / precisa update / já na última versão.
    """
    psection("[VERIFICADOR] Análise de Segurança")

    result: Dict[str, Any] = {
        'ok':                True,
        'warnings':          [],
        'errors':            [],
        'installed_version': None,
        'needs_update':      False,
        'already_latest':    False,
        'trust_reason':      '',   # 'msstore' | 'domain_match' | 'cdn' | 'suspicious'
    }

    homepage      = metadata.get('homepage', '')
    installer_url = metadata.get('installer_url', '')
    app_id        = metadata.get('id', '')
    avail_version = metadata.get('version', '')
    source        = metadata.get('source', 'winget')

    # ── Check 1: Domain Trust ─────────────────────────────────────────────────
    pinfo("Verificando autenticidade do domínio do instalador…")

    if source == 'msstore':
        # Microsoft Store apps are distributed exclusively via Microsoft's
        # signed delivery pipeline.  Every package is reviewed and code-signed
        # by Microsoft before publication — no external URL to validate.
        result['trust_reason'] = 'msstore'
        pok("VERIFICADA — Microsoft Store",
            "(distribuição gerida e assinada pela Microsoft)")

    elif not installer_url:
        msg = "URL do instalador não encontrada — verificação de domínio ignorada"
        result['warnings'].append(msg)
        pwarn(msg)

    elif not homepage:
        msg = "Homepage não encontrada — impossível comparar domínios"
        result['warnings'].append(msg)
        pwarn(msg)

    else:
        hp_domain   = get_registered_domain(homepage)
        inst_domain = get_registered_domain(installer_url)

        pinfo("Homepage domain:",   hp_domain   or '?')
        pinfo("Installer domain:",  inst_domain or '?')

        if hp_domain and hp_domain == inst_domain:
            # ✔ Perfect match — installer on the publisher's own domain
            result['trust_reason'] = 'domain_match'
            pok("Domain Match — instalador no domínio oficial", hp_domain)

        elif is_trusted_cdn(installer_url):
            # ⚠ Different domain but a known-safe CDN/distribution host
            result['trust_reason'] = 'cdn'
            msg = (f"Instalador em CDN de confiança ({inst_domain}) "
                   f"— homepage: {hp_domain}")
            result['warnings'].append(msg)
            pwarn("[CDN CONFIÁVEL]", msg)

        else:
            # ✖ Unknown third-party domain — potential supply-chain risk
            result['trust_reason'] = 'suspicious'
            msg = (f"DOMÍNIO SUSPEITO: homepage={hp_domain!r} ≠ "
                   f"instalador={inst_domain!r}")
            result['errors'].append(msg)
            result['ok'] = False
            perr("[ALERTA CRÍTICO]", msg)
            perr("Instalação BLOQUEADA — use --force para prosseguir a seu risco")

    # ── Check 2: Installed Version ────────────────────────────────────────────
    pinfo("Verificando versão instalada no sistema…")

    target_version = metadata.get('target_version')

    rc, stdout, _ = _run(['winget', 'list', '--id', app_id,
                           '--accept-source-agreements'])
    installed_ver = _parse_installed_version(stdout, app_id)
    result['installed_version'] = installed_ver

    if installed_ver:
        pinfo("Instalada:",   installed_ver)
        if target_version:
            pinfo("Versão alvo:", target_version)
        else:
            pinfo("Disponível:", avail_version)
        compare_ver = target_version if target_version else avail_version
        if installed_ver.strip() == compare_ver.strip():
            result['already_latest'] = True
            pok("Versão pedida já instalada", f"({installed_ver})")
        else:
            result['needs_update'] = True
            if target_version:
                pwarn("Versão diferente instalada",
                      f"{installed_ver} → alvo: {target_version}")
            else:
                pwarn("Atualização disponível",
                      f"{installed_ver} → {avail_version}")
    else:
        pinfo("Não instalado — nova instalação a preparar")

    # ── Summary line ──────────────────────────────────────────────────────────
    print()
    if result['ok']:
        pok(f"VERIFICAÇÃO APROVADA  ({len(result['warnings'])} aviso(s))")
    else:
        perr(f"VERIFICAÇÃO FALHOU  ({len(result['errors'])} erro(s) crítico(s))")

    return result


def _parse_installed_version(output: str, app_id: str) -> Optional[str]:
    """
    Extrai a versão instalada a partir da tabela de `winget list`.
    Usa a posição da coluna 'Version' no cabeçalho para alinhamento correto.
    """
    if not output:
        return None

    lines        = output.strip().splitlines()
    app_id_lower = app_id.lower()

    # Locate the Version column start via header
    header_idx, ver_col = -1, -1
    for i, line in enumerate(lines):
        if re.search(r'\bVersion\b', line, re.IGNORECASE) and \
           re.search(r'\bId\b',      line, re.IGNORECASE):
            header_idx = i
            m = re.search(r'\bVersion\b', line, re.IGNORECASE)
            if m:
                ver_col = m.start()
            break

    data_start = header_idx + 2 if header_idx != -1 else 0

    for line in lines[data_start:]:
        if app_id_lower not in line.lower():
            continue
        # Prefer column-based extraction
        if ver_col > 0 and len(line) > ver_col:
            m = re.match(r'(\S+)', line[ver_col:])
            if m:
                return m.group(1)
        # Fallback: 3rd whitespace-split token
        parts = line.split()
        if len(parts) >= 3:
            return parts[2]

    return None


# ══════════════════════════════════════════════════════════════════════════════
# AGENTE 3 — INSTALADOR
# ══════════════════════════════════════════════════════════════════════════════

def agente_instalador_silent(
    metadata:     Dict[str, Any],
    verification: Dict[str, Any],
    force:        bool = False,
) -> bool:
    """
    Lança o instalador interactivo via winget — o ecrã de instalação abre
    normalmente para que o utilizador possa configurar opções.

    Gates de segurança (avaliados em ordem):
      G1. Verificação falhou E sem --force → BLOQUEIA
      G2. Já na versão mais recente E sem --force → SALTA (sucesso)
      G3. Existem avisos E sem --force → PEDE confirmação ao utilizador
      G4. Procede com:
            winget install|upgrade --id <ID>
    """
    psection("[INSTALADOR] A lançar instalador…")

    app_id = metadata.get('id', '')

    # G1 — Critical security failure
    if not verification['ok'] and not force:
        perr("INSTALAÇÃO BLOQUEADA — verificação de segurança falhou")
        pwarn("Use --force para ignorar (risco assumido pelo utilizador)")
        return False

    # G2 — Already on latest version
    if verification.get('already_latest') and not force:
        pok("Versão mais recente já instalada — nada a fazer")
        return True

    # G3 — Warnings present → interactive confirmation
    if verification['warnings'] and not force:
        print()
        pwarn("Existem avisos de segurança para esta aplicação:")
        for w in verification['warnings']:
            print(f"     {C.YLW}•{C.RST} {w}")
        print(f"\n  {C.BOLD}Deseja continuar mesmo assim? [s/N]{C.RST} ", end='', flush=True)
        try:
            resp = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = 'n'
        if resp not in ('s', 'sim', 'y', 'yes'):
            perr("Instalação cancelada pelo utilizador")
            return False

    # Build winget command
    target_version = metadata.get('target_version')
    # When targeting a specific version, always use 'install' — winget upgrade
    # cannot downgrade; 'install --version' handles both directions correctly.
    if target_version:
        action = 'install'
    else:
        action = 'upgrade' if verification.get('needs_update') else 'install'
    cmd = [
        'winget', action,
        '--id',   app_id,
        '--accept-source-agreements',
        '--accept-package-agreements',
    ]
    if target_version:
        cmd += ['--version', target_version]

    pinfo("Comando:", ' '.join(cmd))
    pinfo("O instalador vai abrir — conclua a instalação na janela que aparecer.")
    print()

    rc, stdout, stderr = _run(cmd, timeout=1800)   # 30 min — tempo para o utilizador configurar

    if rc == 0:
        pok("Instalação concluída com sucesso!", app_id)
        return True

    # Benign exit codes — app already present / no update needed
    BENIGN = {
        -1978335471,  # 0x8A15010F — No applicable update
        -1978335226,  # 0x8A150106 — Higher version installed
        -1978334956,  # 0x8A150214 — No applicable installer (arch/scope)
    }
    if rc in BENIGN or 'already installed' in stdout.lower():
        pok("App já instalada ou atualizada (sem alterações necessárias)")
        return True

    perr(f"Falha na instalação (código de saída: {rc})")
    if stderr.strip():
        pinfo("Stderr:", stderr.strip()[:240])
    return False


# ══════════════════════════════════════════════════════════════════════════════
# SECURITY REPORT — Visual Terminal Output
# ══════════════════════════════════════════════════════════════════════════════

def print_security_report(
    app_name:     str,
    metadata:     Optional[Dict[str, Any]],
    verification: Optional[Dict[str, Any]],
    success:      bool,
) -> None:
    """
    Imprime um relatório visual completo numa box de caracteres Unicode
    com informações de segurança, versão e resultado final da instalação.
    """
    W = 60   # inner box width (visual characters)

    def row(text: str) -> None:
        """Print a box row, padding text to width W accounting for ANSI codes."""
        visual_len = len(_strip_ansi(text))
        padding    = max(0, W - visual_len)
        print(f"{C.BOLD}║{C.RST}{text}{' ' * padding}{C.BOLD}║{C.RST}")

    def divider() -> None:
        print(f"{C.BOLD}╠{'═' * W}╣{C.RST}")

    print(f"\n{C.BOLD}╔{'═' * W}╗{C.RST}")
    row(f"{C.BOLD}  RELATÓRIO DE SEGURANÇA — {app_name.upper()}{C.RST}")
    divider()

    # Metadata block
    if metadata:
        row(f"  {'ID':<13}{C.CYN}{metadata.get('id',        'N/A')}{C.RST}")
        row(f"  {'Publisher':<13}{metadata.get('publisher', 'N/A')}")
        row(f"  {'Versão':<13}{metadata.get('version',      'N/A')}")
        tv = metadata.get('target_version')
        if tv:
            row(f"  {'Versão alvo':<13}{C.YLW}{tv}{C.RST}  {C.DIM}(versão específica pedida){C.RST}")
        hp = (metadata.get('homepage') or 'N/A')[:44]
        row(f"  {'Homepage':<13}{C.DIM}{hp}{C.RST}")
        # Source row — shows origin clearly
        src = metadata.get('source', 'winget')
        if src == 'msstore':
            src_display = f"{C.BLU}Microsoft Store{C.RST}  {C.DIM}(loja oficial){C.RST}"
        else:
            src_display = f"{C.CYN}winget — Site do Fabricante{C.RST}"
        row(f"  {'Fonte':<13}{src_display}")
    else:
        row(f"  {C.YLW}App não encontrada no winget{C.RST}")

    divider()

    # Security checks block
    if verification:
        trust = verification.get('trust_reason', '')

        # Domain / origin status row
        if trust == 'msstore':
            dom = (f"  Origem:      {C.GRN}✔ Microsoft Store "
                   f"— verificado pela Microsoft{C.RST}")
        elif trust == 'domain_match':
            dom = f"  Origem:      {C.GRN}✔ Domínio oficial confirmado{C.RST}"
        elif trust == 'cdn':
            dom = f"  Origem:      {C.YLW}⚠ CDN de confiança (domínio diferente){C.RST}"
        elif trust == 'suspicious':
            dom = f"  Origem:      {C.RED}✖ ALERTA — domínio suspeito{C.RST}"
        else:
            # No URL found but not msstore either
            dom = f"  Origem:      {C.YLW}⚠ URL não encontrada — não verificado{C.RST}"
        row(dom)

        if verification.get('already_latest'):
            ver = f"  Versão:      {C.GRN}✔ Já na versão mais recente{C.RST}"
        elif verification.get('needs_update'):
            ver = f"  Versão:      {C.YLW}⚠ Atualização aplicada{C.RST}"
        else:
            ver = f"  Versão:      {C.CYN}ℹ Nova instalação{C.RST}"
        row(ver)

        for msg in verification.get('errors', []) + verification.get('warnings', []):
            row(f"  {C.YLW}▸ {msg[:W - 5]}{C.RST}")

    divider()

    # Final result
    if success:
        row(f"  {C.GRN}{C.BOLD}✔  SUCESSO{C.RST}")
    else:
        row(f"  {C.RED}{C.BOLD}✖  FALHOU / BLOQUEADO{C.RST}")

    print(f"{C.BOLD}╚{'═' * W}╝{C.RST}")


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def agente_dependencias(metadata: Dict[str, Any]) -> bool:
    """
    Verifica se as dependências declaradas pelo pacote estão instaladas.
    Instala as que faltam após confirmação do utilizador.
    Retorna True para continuar, False para abortar.
    """
    psection("[DEPENDÊNCIAS] Verificando dependências do pacote…")

    deps = metadata.get('dependencies', [])
    if not deps:
        pok("Nenhuma dependência declarada pelo pacote.")
        return True

    pinfo(f"{len(deps)} dependência(s) declarada(s):")
    for d in deps:
        print(f"    • {d}")

    # Check which are missing
    missing = []
    for dep_id in deps:
        rc, stdout, _ = _run(['winget', 'list', '--id', dep_id,
                               '--accept-source-agreements'])
        if rc != 0 or dep_id.lower() not in stdout.lower():
            missing.append(dep_id)
            pwarn("Em falta:", dep_id)
        else:
            pok("Instalada:", dep_id)

    if not missing:
        pok("Todas as dependências estão instaladas.")
        return True

    print()
    pwarn(f"{len(missing)} dependência(s) em falta:")
    for dep in missing:
        print(f"    • {C.YLW}{dep}{C.RST}")
    print()

    try:
        answer = input(
            f"  {C.BOLD}Instalar dependências em falta antes de continuar? [s/n]{C.RST} › "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = 'n'

    if answer not in ('s', 'sim', 'y', 'yes'):
        pwarn("Dependências ignoradas — a instalação pode falhar a meio.")
        return True  # não é crítico, deixa continuar

    for dep_id in missing:
        pinfo("A instalar dependência:", dep_id)
        cmd = ['winget', 'install', '--id', dep_id, '--accept-source-agreements']
        rc, _, stderr = _run(cmd, timeout=900)
        if rc == 0:
            pok("Dependência instalada:", dep_id)
        else:
            perr("Falha ao instalar dependência:", dep_id)
            perr("Detalhe:", stderr[:120])

    return True


def process_app(app_name: str, force: bool = False,
                target_version: Optional[str] = None) -> bool:
    """Executa o pipeline completo de 4 agentes para uma aplicação."""
    pheader(f"PROCESSANDO: {app_name.upper()}")

    # Stage 1 — Pesquisador
    metadata = agente_pesquisador(app_name, target_version=target_version)
    if not metadata:
        print_security_report(app_name, None, None, False)
        return False

    # Stage 2 — Verificador
    verification = agente_verificador(metadata)

    # Stage 3 — Dependências
    agente_dependencias(metadata)

    # Stage 4 — Instalador
    success = agente_instalador_silent(metadata, verification, force=force)

    # Report
    print_security_report(app_name, metadata, verification, success)
    return success


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    enable_ansi()
    args = sys.argv[1:]

    # Help
    if not args or '--help' in args or '-h' in args:
        print(f"\n{C.BOLD}win_secure_installer.py{C.RST}  |  Instalador Agêntico Windows")
        print(f"\n{C.BOLD}Uso:{C.RST}  python win_secure_installer.py <app> [--app-version <v>] [--force]")
        print(f"      python win_secure_installer.py <app1> [app2 ...] [--force]")
        print(f"\n{C.BOLD}Exemplos:{C.RST}")
        print("  python win_secure_installer.py python --app-version 3.11.9")
        print("  python win_secure_installer.py discord")
        print("  python win_secure_installer.py discord vscode vlc spotify")
        print("  python win_secure_installer.py flstudio --force")
        print(f"\n{C.BOLD}Flags:{C.RST}")
        print("  --app-version <v>  Instala a versão exacta especificada (ex: 3.11.9)")
        print("  --force            Ignora erros de segurança e reinstala se já atualizado")
        print("  --help             Mostra esta ajuda\n")
        sys.exit(0)

    force = '--force' in args

    # Extract --app-version <value>
    target_version: Optional[str] = None
    if '--app-version' in args:
        idx = args.index('--app-version')
        if idx + 1 < len(args) and not args[idx + 1].startswith('--'):
            target_version = args[idx + 1]
        else:
            perr("--app-version requer um valor (ex: --app-version 3.11.9)")
            sys.exit(1)

    apps = [a for a in args if not a.startswith('--')
            and a != (target_version or '')]

    if not apps:
        perr("Nenhum app especificado. Use --help para ajuda.")
        sys.exit(1)

    if target_version and len(apps) > 1:
        perr("--app-version só pode ser usado com uma aplicação de cada vez")
        sys.exit(1)

    # ── Startup ───────────────────────────────────────────────────────────────
    pheader("WIN SECURE INSTALLER  |  3-Stage Agentic Pipeline")

    if not is_admin():
        pwarn(
            "AVISO: Sem privilégios de Administrador!",
            "\n         Certas apps (FL Studio, drivers, VMs) requerem elevação."
            "\n         → Clique com botão direito → 'Executar como Administrador'"
        )
    else:
        pok("A correr como Administrador")

    if not check_winget():
        perr("winget não encontrado!",
             "Instale o 'App Installer' na Microsoft Store.")
        sys.exit(1)

    pinfo(f"Apps a processar: {C.BOLD}{', '.join(apps)}{C.RST}")
    if target_version:
        pinfo(f"Versão alvo: {C.BOLD}{target_version}{C.RST}")
    if force:
        pwarn("Modo --force ATIVO — avisos de segurança serão ignorados")

    # ── Run pipeline for each app ─────────────────────────────────────────────
    results: Dict[str, bool] = {}
    for app in apps:
        results[app] = process_app(app, force=force, target_version=target_version)

    # ── Final Summary ─────────────────────────────────────────────────────────
    pheader("RESUMO FINAL")

    succeeded = sum(1 for v in results.values() if v)
    failed    = len(results) - succeeded

    for app, ok in results.items():
        if ok:
            pok(app)
        else:
            perr(app)

    print()
    pinfo(
        f"Total: {C.BOLD}{len(results)}{C.RST}  |  "
        f"Sucesso: {C.GRN}{C.BOLD}{succeeded}{C.RST}  |  "
        f"Falha: {C.RED}{C.BOLD}{failed}{C.RST}"
    )
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
