#!/bin/bash

ROOT_CRL="PKI/root/crl/root.crl.pem"
INTER_CRL="PKI/intermediate/crl/intermediate.crl.pem"
OUT_CRL="PKI/intermediate/crl/full-chain.crl.pem"

# Verifica se os ficheiros existem
if [[ ! -f "$ROOT_CRL" || ! -f "$INTER_CRL" ]]; then
    echo "❌ Uma das CRLs não existe. Verifica as paths:"
    echo "Root: $ROOT_CRL"
    echo "Intermediate: $INTER_CRL"
    exit 1
fi

# Concatena as CRLs
cat "$ROOT_CRL" "$INTER_CRL" > "$OUT_CRL"
echo "✅ CRLs concatenadas com sucesso: $OUT_CRL"

# Mostra os Issuers incluídos para verificação
echo "📜 Issuers presentes:"
openssl crl -in "$OUT_CRL" -text -noout | grep 'Issuer'


