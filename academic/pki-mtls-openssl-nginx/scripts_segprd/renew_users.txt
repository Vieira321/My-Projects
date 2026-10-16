#!/bin/bash

USER_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/../..")"

BASE_DIR="$PROJECT_ROOT/PKI"
INT_CA_DIR="$BASE_DIR/intermediate"
USER_DIR="$BASE_DIR/users/users/$USER_NAME"
KEY_FILE="$USER_DIR/$USER_NAME.key.pem"
CSR_FILE="$USER_DIR/$USER_NAME.csr.renovado.pem"
NEW_CERT_FILE="$USER_DIR/$USER_NAME.cert.renovado.pem"
P12_FILE="$USER_DIR/$USER_NAME.renovado.p12"

if [ -z "$USER_NAME" ]; then
  echo "⚠  Usa: $0 <nome_utilizador>"
  exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
  echo "❌ Chave privada não encontrada: $KEY_FILE"
  exit 1
fi

echo "📝 A gerar novo CSR para $USER_NAME com chave antiga..."
openssl req -new -key "$KEY_FILE" -out "$CSR_FILE"

echo "🔐 A assinar novo certificado com a Intermediate CA..."
openssl ca -batch -config "$INT_CA_DIR/openssl.cnf" \
    -extensions usr_cert \
    -days 375 -notext -md sha256 \
    -in "$CSR_FILE" \
    -out "$NEW_CERT_FILE"

chmod 444 "$NEW_CERT_FILE"

echo "📦 A gerar novo ficheiro PKCS#12 (.p12)..."
openssl pkcs12 -export \
    -inkey "$KEY_FILE" \
    -in "$NEW_CERT_FILE" \
    -certfile "$INT_CA_DIR/certs/ca-chain.cert.pem" \
    -out "$P12_FILE"

chmod 444 "$P12_FILE"

echo "✅ Certificado renovado com sucesso!"
echo "📂 Ficheiros atualizados:"
echo "  - Novo certificado: $NEW_CERT_FILE"
echo "  - Novo ficheiro .p12: $P12_FILE"
