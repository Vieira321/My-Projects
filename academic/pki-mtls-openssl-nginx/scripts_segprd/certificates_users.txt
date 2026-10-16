#!/bin/bash

USER_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/../..")"

BASE_DIR="$PROJECT_ROOT/PKI"
INT_CA_DIR="$BASE_DIR/intermediate"
USER_DIR="$BASE_DIR/users/users/$USER_NAME"

if [ -z "$USER_NAME" ]; then
  echo "⚠  Usa: $0 <nome_utilizador>"
  exit 1
fi

mkdir -p "$USER_DIR"

echo "🔐 A gerar chave privada para $USER_NAME..."
openssl genrsa -out "$USER_DIR/$USER_NAME.key.pem" 2048
chmod 400 "$USER_DIR/$USER_NAME.key.pem"

echo "📝 A gerar CSR para $USER_NAME..."
openssl req -new -key "$USER_DIR/$USER_NAME.key.pem" \
    -out "$USER_DIR/$USER_NAME.csr.pem"

echo "✅ A assinar o certificado com a Intermediate CA..."
openssl ca -batch -config "$INT_CA_DIR/openssl.cnf" \
    -extensions usr_cert \
    -days 375 -notext -md sha256 \
    -in "$USER_DIR/$USER_NAME.csr.pem" \
    -out "$USER_DIR/$USER_NAME.cert.pem"

chmod 444 "$USER_DIR/$USER_NAME.cert.pem"

openssl pkcs12 -export \
    -inkey "$USER_DIR/$USER_NAME.key.pem" \
    -in "$USER_DIR/$USER_NAME.cert.pem" \
    -certfile "$INT_CA_DIR/certs/ca-chain.cert.pem" \
    -out "$USER_DIR/$USER_NAME.p12"

chmod 444 "$USER_DIR/$USER_NAME.p12"

echo "🎉 Certificado criado com sucesso para $USER_NAME em:"
echo "    - Chave privada: $USER_DIR/$USER_NAME.key.pem"
echo "    - Certificado:   $USER_DIR/$USER_NAME.cert.pem"
echo "    - PKCS#12:       $USER_DIR/$USER_NAME.p12"


