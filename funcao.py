import smtplib
from email.mime.text import MIMEText
import jwt
import datetime
from main import app

senha_secreta = app.config['SECRET_KEY']

def gerar_token(id_usuario):
    payload = {'id_usuario': id_usuario, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')

    return token


def remover_bearer(token):
    if token.startswith('Bearer '):
        return token[len('Bearer '):]
    else:
        return token

def enviando_email(destinatario, assunto, mensagem):
    user = 'caiquefachinigoncalves@gmail.com'
    senha = 'vzpa yqgs sxbi wgih'

    msg = MIMEText(mensagem)
    msg['From'] = user
    msg['To'] =  destinatario
    msg['Subject'] = assunto

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, senha)
    server.sendmail(user, destinatario, msg.as_string())
    server.quit()

def verificar_senha_forte(senha):
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"

    tem_minusculo = False
    tem_maiusculo = False
    tem_numero = False
    tem_especial = False

    numeros = "0123456789"
    maiusculas = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    minusculas = "abcdefghijklmnopqrstuvwxyz"
    especias = "!@#$%^&*()_+-=[]{}|;:,.<>/?`~"


    for char in senha:
        if char in maiusculas:
            tem_maiusculo = True
        elif char in minusculas:
            tem_minusculo = True
        elif char in numeros:
            tem_numero = True
        elif char in especias:
            tem_especial = True


    erros = []
    if not tem_maiusculo:
        erros.append("letra maiúscula")
    if not tem_minusculo:
        erros.append("letra minúscula")
    if not tem_numero:
        erros.append("número")
    if not tem_especial:
        erros.append("especiais")

    if erros:
        return False, "Falta: " + ", ".join(erros)

    return True, "Senha válida"