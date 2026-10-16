#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/PKI/users"
USERS_DIR="$PROJECT_ROOT/PKI/users/users"

pause() {
  echo
  read -p "Pressiona Enter para continuar…"
}

testar_acesso() {
  read -p "🔤 Nome do utilizador a testar (com certificado válido): " USERNAME
  CERT="$USERS_DIR/$USERNAME/$USERNAME.cert.pem"
  KEY="$USERS_DIR/$USERNAME/$USERNAME.key.pem"
  CA_CHAIN="$PROJECT_ROOT/PKI/intermediate/certs/ca-chain.cert.pem"

  if [[ ! -f "$CERT" || ! -f "$KEY" ]]; then
    echo "❌ Certificado ou chave não encontrados para $USERNAME."
    pause
    return
  fi

  echo "🚀 A testar acesso via curl..."
  curl -v https://servidor \
    --cert "$CERT" \
    --key "$KEY" \
    --cacert "$CA_CHAIN"

  pause
}

listar_utilizadores() {
  echo "📄 Utilizadores existentes:"
  ls -1 "$USERS_DIR"
  pause
}

ver_validade_certificado() {
  read -p "👤 Nome do utilizador: " USERNAME
  CERT="$USERS_DIR/$USERNAME/$USERNAME.cert.pem"

  if [[ ! -f "$CERT" ]]; then
    echo "❌ Certificado não encontrado para $USERNAME."
    pause
    return
  fi

  echo "📆 Data de expiração do certificado de $USERNAME:"
  openssl x509 -in "$CERT" -noout -enddate
  pause
}

renovar_certificado_menu() {
  while true; do
    clear
    echo "===== 🔄 Renovar Certificado ====="
    echo "1) Renovar certificado de utilizador válido"
    echo "2) Reemitir certificado de utilizador revogado"
    echo "3) Voltar ao menu principal"
    echo "=================================="
    read -p "Escolha uma opção [1-3]: " escolha

    case $escolha in
      1)
        read -p "👤 Nome do utilizador a renovar: " nome
        "$SCRIPTS_DIR/renew_users.sh" "$nome"
        pause
        ;;
      2)
        read -p "👤 Nome do utilizador a reemitir (revogado): " nome
        "$SCRIPTS_DIR/reissue_revoked_users.sh" "$nome"
        pause
        ;;
      3)
        break
        ;;
      *)
        echo "❗ Opção inválida."
        pause
        ;;
    esac
  done
}

while true; do
  clear
  echo "==== 🛡 PKI MENU - Segurança e Privacidade dos Dados ===="
  echo "1) Criar novo utilizador"
  echo "2) Revogar certificado de utilizador"
  echo "3) Renovar/Reemitir certificado de utilizador"
  echo "4) Testar acesso (curl)"
  echo "5) Listar utilizadores existentes"
  echo "6) Ver validade de um certificado de utilizador"
  echo "7) Sair"
  echo "========================================================="
  read -p "Escolha uma opção [1-7]: " opcao

  case $opcao in
    1)
      read -p "👤 Nome do novo utilizador: " nome
      "$SCRIPTS_DIR/certificates_users.sh" "$nome"
      pause
      ;;
    2)
      read -p "👤 Nome do utilizador a revogar: " nome
      "$SCRIPTS_DIR/revoke_users.sh" "$nome"
      pause
      ;;
    3)
      renovar_certificado_menu
      ;;
    4)
      testar_acesso
      ;;
    5)
      listar_utilizadores
      ;;
    6)
      ver_validade_certificado
      ;;
    7)
      echo "👋 A sair..."
      exit 0
      ;;
    *)
      echo "❗ Opção inválida."
      pause
      ;;
  esac
done
