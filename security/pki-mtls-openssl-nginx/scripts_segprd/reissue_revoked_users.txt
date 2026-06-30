#!/bin/bash

USER_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/../..")"

BASE_DIR="$PROJECT_ROOT/PKI"
INT_CA_DIR="$BASE_DIR/intermediate"
USER_DIR="$BASE_DIR/users/users/$USER_NAME"

KEY_FILE="$USER_DIR/$USER_NAME.key.pem"
OLD_CERT_FILE="$USER_DIR/$USER_NAME.cert.pem"
NEW_CSR_FILE="$USER_DIR/$USER_NAME.csr.reissue.pem"
NEW_CERT_FILE="$USER_DIR/$USER_NAME.cert.reissue.pem"
NEW_P12_FILE="$USER_DIR/$USER_NAME.reissue.p12"

if [[ -z "$USER_NAME" ]]; then
    echo "⚠  Usa: $0 <nome_utilizador>"
    exit 1
fi

if [[ ! -f "$KEY_FILE" ]]; then
    echo "❌ Chave privada não encontrada: $KEY_FILE"
    exit 1
fi

if [[ ! -f "$OLD_CERT_FILE" ]]; then
    echo "❌ Certificado antigo não encontrado: $OLD_CERT_FILE"
    exit 1
fi

# Verifica se o certificado está revogado na CRL
SERIAL_HEX=$(openssl x509 -in "$OLD_CERT_FILE" -noout -serial | cut -d= -f2 >
IS_REVOKED=$(openssl crl -in "$INT_CA_DIR/crl/intermediate.crl.pem" -text -n>

if [[ -z "$IS_REVOKED" ]]; then
    echo "❗ O certificado de $USER_NAME não está revogado. Usa o script de >
    exit 1
fi

echo "🔐 O certificado antigo foi revogado. A proceder à reemissão..."

# Backup dos ficheiros antigos
mv "$OLD_CERT_FILE" "$USER_DIR/${USER_NAME}.cert.revogado.pem"
[ -f "$USER_DIR/$USER_NAME.p12" ] && mv "$USER_DIR/$USER_NAME.p12" "$USER_DI>
[ -f "$USER_DIR/$USER_NAME.csr.pem" ] && mv "$USER_DIR/$USER_NAME.csr.pem" ">

echo "📝 A gerar novo CSR com a chave existente..."
openssl req -new -key "$KEY_FILE" -out "$NEW_CSR_FILE"

echo "✅ A assinar novo certificado com a CA Intermédia..."
openssl ca -batch -config "$INT_CA_DIR/openssl.cnf" \
    -extensions usr_cert \
    -days 375 -notext -md sha256 \
    -in "$NEW_CSR_FILE" \
    -out "$NEW_CERT_FILE" \
    -passin pass:kali

chmod 444 "$NEW_CERT_FILE"

echo "📦 A gerar novo ficheiro PKCS#12 (.p12)..."
openssl pkcs12 -export \
    -inkey "$KEY_FILE" \
    -in "$NEW_CERT_FILE" \
    -certfile "$INT_CA_DIR/certs/ca-chain.cert.pem" \
    -out "$NEW_P12_FILE"

chmod 444 "$NEW_P12_FILE"

# 🧼 Substituir o .cert.pem e .p12 antigos pelos novos
cp "$NEW_CERT_FILE" "$USER_DIR/$USER_NAME.cert.pem"
cp "$NEW_P12_FILE" "$USER_DIR/$USER_NAME.p12"

echo "🎉 Reemissão completa para $USER_NAME"
echo "  - Novo certificado: $USER_DIR/$USER_NAME.cert.pem"
echo "  - Novo .p12:        $USER_DIR/$USER_NAME.p12"
echo "  - Antigo certificado guardado como: $USER_NAME.cert.revogado.pem"

