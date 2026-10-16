from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    cert = request.headers.get('X-SSL-CERT')
    verify = request.headers.get('X-SSL-VERIFY')

    if verify == "SUCCESS" and cert:
        return f"🔐 Bem-vindo, certificado:\n\n{cert}"
    return "❌ Acesso negado. Certificado não encontrado."

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)