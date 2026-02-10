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