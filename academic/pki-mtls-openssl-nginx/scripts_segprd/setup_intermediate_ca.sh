#!/bin/bash

# Caminhos
BASE_DIR=PKI
ROOT_CA_DIR=$BASE_DIR/root
INT_CA_DIR=$BASE_DIR/intermediate

# Criar estrutura da Intermediate CA
mkdir -p $INT_CA_DIR/{certs,crl,csr,newcerts,private}
touch $INT_CA_DIR/index.txt
echo 1000 > $INT_CA_DIR/serial
echo 1000 > $INT_CA_DIR/crlnumber

# Gerar chave privada da Intermediate CA
openssl genrsa -aes256 -out $INT_CA_DIR/private/intermediate.key.pem 4096
chmod 400 $INT_CA_DIR/private/intermediate.key.pem

# Criar CSR da Intermediate CA
openssl req -config $INT_CA_DIR/openssl.cnf \
    -new -sha256 \
    -key $INT_CA_DIR/private/intermediate.key.pem \
    -out $INT_CA_DIR/csr/intermediate.csr.pem

# Assinar o certificado da Intermediate CA com a Root CA
openssl ca -config $ROOT_CA_DIR/openssl.cnf \
    -extensions v3_intermediate_ca \
    -days 3650 -notext -md sha256 \
    -in $INT_CA_DIR/csr/intermediate.csr.pem \
    -out $INT_CA_DIR/certs/intermediate.cert.pem

chmod 444 $INT_CA_DIR/certs/intermediate.cert.pem

# Criar cadeia de certificados (intermediate + root)
if [ -f $INT_CA_DIR/certs/intermediate.cert.pem ]; then
    echo "[✔] Certificado da Intermediate CA criado com sucesso."
    cat $INT_CA_DIR/certs/intermediate.cert.pem \
        $ROOT_CA_DIR/certs/ca.cert.pem > $INT_CA_DIR/certs/ca-chain.cert.pem
    chmod 444 $INT_CA_DIR/certs/ca-chain.cert.pem
    echo "[✔] Ficheiro ca-chain.cert.pem criado."
else
    echo "[✘] Algo correu mal. O certificado não foi criado."
fi

