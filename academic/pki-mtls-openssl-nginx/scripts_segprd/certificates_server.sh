#!/bin/bash

set -e

# Diretórios
SERVER_NAME=servidor
BASE_DIR=$(pwd)
INT_CA_DIR="$BASE_DIR/../intermediate"
SERVER_DIR="$BASE_DIR"

mkdir -p "$SERVER_DIR"

# Geração da chave privada
openssl genrsa -out "$SERVER_DIR/$SERVER_NAME.key.pem" 2048
chmod 400 "$SERVER_DIR/$SERVER_NAME.key.pem"

# Geração do CSR
openssl req -new -key "$SERVER_DIR/$SERVER_NAME.key.pem" \
    -out "$SERVER_DIR/$SERVER_NAME.csr.pem" \
    -subj "/CN=$SERVER_NAME"

# Assinatura do certificado com a Intermediate CA
cd "$INT_CA_DIR"
openssl ca -config openssl.cnf \
      -extensions server_cert -days 375 -notext -md sha256 \
      -in "$SERVER_DIR/$SERVER_NAME.csr.pem" \
      -out "$SERVER_DIR/$SERVER_NAME.cert.pem"

chmod 444 "$SERVER_DIR/$SERVER_NAME.cert.pem"

