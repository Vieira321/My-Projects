# PKI with Mutual TLS (OpenSSL · NGINX · Flask)

A complete **Public Key Infrastructure** built and automated from scratch for the *Segurança e Privacidade dos Dados* (Data Security & Privacy) course of the MEng in Computer Engineering.

**Authors:** Diogo Vieira (1240448) · João Monteiro (1240469) — April 2025
**Full report:** [`report/SEGPRD-Project1-1240469-1240448.pdf`](./report/)

---

## What this project is

The system implements a two‑tier certificate authority and uses it to enforce **certificate‑based mutual authentication (mTLS)** in front of a web application:

- **Root CA** — the organisation's offline trust anchor. 4096‑bit RSA key, self‑signed, long validity. Signs nothing except the Intermediate CA.
- **Intermediate CA** — the working CA that issues all end‑entity certificates (server and users), so the Root key can stay protected.
- **NGINX reverse proxy** — terminates TLS and requires a valid client certificate signed by the chain before forwarding any request.
- **Flask backend** — the protected application, only reachable through the mTLS‑enforcing proxy.
- **Lifecycle automation** — Bash + OpenSSL scripts to issue, revoke (with **CRL** generation/concatenation), renew, and reissue certificates, all exposed through an interactive `menu.sh`.

## Architecture

```
            ┌────────────┐
            │  Root CA   │   self-signed, offline trust anchor
            └─────┬──────┘
                  │ signs
            ┌─────▼──────────┐
            │ Intermediate CA│   issues end-entity certs + maintains CRL
            └─────┬──────────┘
        ┌─────────┴──────────┐
        │ signs              │ signs
 ┌──────▼───────┐     ┌──────▼───────┐
 │ Server cert  │     │  User certs  │
 └──────┬───────┘     └──────┬───────┘
        │                    │ presents cert
 ┌──────▼─────────────────────▼──────┐
 │  NGINX  — verifies client cert     │  mutual TLS (mTLS)
 │  against ca-chain, then proxies →  │
 └──────────────────┬─────────────────┘
                    │
             ┌──────▼──────┐
             │  Flask app  │   protected backend
             └─────────────┘
```

## Scripts

| Script | Purpose |
|---|---|
| `setup_root_ca.sh` | Build the Root CA: directory tree, 4096‑bit key, self‑signed certificate |
| `setup_intermediate_ca.sh` | Build the Intermediate CA and sign it with the Root |
| `certificates_server.sh` | Issue the server certificate used by NGINX |
| `certificates_users.sh` | Issue a new end‑entity (user) certificate |
| `revoke_users.sh` | Revoke a user certificate and update the CRL |
| `concat_crls.sh` | Concatenate Root + Intermediate CRLs into a single chain CRL |
| `renew_users.sh` | Renew a still‑valid user certificate |
| `reissue_revoked_users.sh` | Reissue a certificate for a previously revoked user |
| `menu.sh` | Interactive entry point that ties all of the above together |
| `app.py` | Flask backend served behind the mTLS proxy |
| `-etc-nginx-sites-available-pki-app.txt` | NGINX site configuration (mTLS verification) |

> The `*.txt` files mirror each `*.sh`/config for easy reading on GitHub without download.

## How to run (Linux)

```bash
chmod +x *.sh

# 1) Trust chain
./setup_root_ca.sh
./setup_intermediate_ca.sh

# 2) Server certificate + NGINX
./certificates_server.sh
sudo cp ./-etc-nginx-sites-available-pki-app.txt /etc/nginx/sites-available/pki-app
sudo ln -s /etc/nginx/sites-available/pki-app /etc/nginx/sites-enabled/
echo "127.0.0.1  servidor" | sudo tee -a /etc/hosts
sudo nginx -t && sudo systemctl reload nginx

# 3) Backend + management
python3 app.py
./menu.sh
```

The scripts build a `PKI/` working tree (`root/`, `intermediate/`, `server/`, `users/`). Test access with a user's certificate:

```bash
curl -v https://servidor \
  --cert  PKI/users/users/<name>/<name>.cert.pem \
  --key   PKI/users/users/<name>/<name>.key.pem \
  --cacert PKI/intermediate/certs/ca-chain.cert.pem
```

**Requirements:** `openssl`, `nginx`, Python 3 + Flask, a Linux environment.

## Skills demonstrated

- Two‑tier CA / trust‑chain design and the reasoning behind separating Root and Intermediate
- X.509 certificate issuance, revocation, renewal, reissuance
- CRL generation and chaining
- mTLS client authentication at the proxy layer
- Security automation in Bash with OpenSSL configuration policies
