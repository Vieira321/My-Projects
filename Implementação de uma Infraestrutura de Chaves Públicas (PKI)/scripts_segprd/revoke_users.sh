#!/bin/bash

USER_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/../..")"

INT_CA_DIR="$PROJECT_ROOT/PKI/intermediate"
ROOT_CA_DIR="$PROJECT_ROOT/PKI/root"
USER_DIR="$PROJECT_ROOT/PKI/users/users/$USER_NAME"
CERT_FILE="$USER_DIR/$USER_NAME.cert.pem"
FULL_CHAIN_CRL="$INT_CA_DIR/crl/full-chain.crl.pem"

if [ -z "$USER_NAME" ]; then
  echo "⚠  Usa: $0 <nome_utilizador>"
  exit 1
fi

if [ ! -f "$CERT_FILE" ]; then
  echo "❌ Certificado de $USER_NAME não encontrado em $CERT_FILE"
  exit 1
fi

echo "🛑 A revogar o certificado de $USER_NAME..."
openssl ca -config "$INT_CA_DIR/openssl.cnf" -revoke "$CERT_FILE" -passin pa>

echo "🔄 A gerar nova CRL da Intermédia..."
openssl ca -config "$INT_CA_DIR/openssl.cnf" \
    -gencrl \
    -out "$INT_CA_DIR/crl/intermediate.crl.pem" \
    -passin pass:kali

echo "🔄 A gerar nova CRL da Root..."
openssl ca -config "$ROOT_CA_DIR/openssl.cnf" \
    -gencrl \
    -out "$ROOT_CA_DIR/crl/root.crl.pem" \
    -passin pass:kali

echo "📦 A concatenar CRLs (Root + Intermédia) em $FULL_CHAIN_CRL"
cat "$ROOT_CA_DIR/crl/root.crl.pem" "$INT_CA_DIR/crl/intermediate.crl.pem" >>

chmod 444 "$INT_CA_DIR/crl/intermediate.crl.pem"
chmod 444 "$ROOT_CA_DIR/crl/root.crl.pem"
chmod 444 "$FULL_CHAIN_CRL"

echo "🚀 A reiniciar o NGINX..."
sudo nginx -t && sudo systemctl reload nginx

echo "✅ Certificado revogado e NGINX atualizado com nova CRL!"

