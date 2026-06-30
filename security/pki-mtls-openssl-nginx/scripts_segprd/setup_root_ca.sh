#!/bin/bash

# Definir diretório base
BASE_DIR=PKI
ROOT_CA_DIR=$BASE_DIR/root

# Criar estrutura de diretórios
mkdir -p $ROOT_CA_DIR/{certs,crl,newcerts,private}
touch $ROOT_CA_DIR/index.txt
echo 1000 > $ROOT_CA_DIR/serial

# Gerar chave privada da Root CA
openssl genrsa -aes256 -out $ROOT_CA_DIR/private/ca.key.pem 4096
chmod 400 $ROOT_CA_DIR/private/ca.key.pem

# Criar certificado da Root CA (autoassinado)
openssl req -config $ROOT_CA_DIR/openssl.cnf \
    -key $ROOT_CA_DIR/private/ca.key.pem \
    -new -x509 -days 7300 -sha256 -extensions v3_ca \
    -out $ROOT_CA_DIR/certs/ca.cert.pem

chmod 444 $ROOT_CA_DIR/certs/ca.cert.pem



