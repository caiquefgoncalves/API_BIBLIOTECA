from flask import jsonify, request, Response
from main import app, con, bcrypt
from funcao import verificar_senha_forte
from fpdf import FPDF
import os

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



'LIVROS'
@app.route('/livro', methods=['GET'])
def livro():
    try:
        cursor= con.cursor()
        cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM livros')
        livros = cursor.fetchall()

        livros_lis = []

        for livro in livros:
            livros_lis.append({
                'id_livro': livro[0],
                'titulo': livro[1],
                'autor': livro[2],
                'ano_publicacao': livro[3]
            })
        return jsonify(mensagem='Lista de Livros', livros=livros_lis)
    except Exception as e:
        return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
    finally:
        cursor.close()






@app.route('/criar_livro', methods=['POST'])
def criar_livro():


        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        ano_publicacao = request.form.get('ano_publicacao')
        imagem = request.files.get('imagem')

        try:

            cursor = con.cursor()
            cursor.execute("SELECT 1 FROM livros WHERE titulo = ? ", (titulo,))
            if cursor.fetchone():
                return jsonify({"error": "Livro já cadastrado"}), 400
            cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?,?,?) RETURNING id_livro",
                                                        (titulo, autor, ano_publicacao))


            codigo_livro = cursor.fetchone()[0]


            con.commit()

            caminho_imagem = None

            if imagem:
                nome_imagem = f'{codigo_livro}.jpg'
                caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
                os.makedirs(caminho_imagem_destino, exist_ok= True)
                caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
                imagem.save(caminho_imagem)


            return jsonify({
                'message': 'Livro cadastrado com sucesso!',
                'livro': {
                    'titulo': titulo,
                    'autor': autor,
                    'ano_publicacao': ano_publicacao
                }
            }),201



        except Exception as e:
            return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
        finally:
            cursor.close()



@app.route('/editar_livro/<int:id>', methods=['PUT'])
def editar_livros(id):

    cursor = con.cursor()

    cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao from livros WHERE id_livro = ?', (id,))

    tem_livro = cursor.fetchone()
    if not tem_livro:
        cursor.close()
        return jsonify({"error": "Livro não encontrado!"}), 404

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute('UPDATE livros set titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livro = ?', (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({"message": "Livro atualizado com sucesso",
                    'livro': {
                        'titulo': titulo,
                        'autor': autor,
                        'ano_publicacao': ano_publicacao,
                        'id_livro': id
                            }
                  })


@app.route('/apagar_livro/<int:id>', methods=['DELETE'] )
def apagar_livros(id):

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM livros WHERE id_livro = ?', (id,))
    livro_existe = cursor.fetchone()

    if not livro_existe:
        cursor.close()
        return jsonify({"error": "Livro não encontrado!"}), 404


    cursor.execute("DELETE FROM livros WHERE id_livro = ?", (id,))

    con.commit()
    cursor.close()

    return jsonify({"message": "Livro apagado com sucesso!", 'id_livro': id})










'USUÁRIOS'

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        cursor = con.cursor()
        cursor.execute('SELECT id_usuario, nome, usuario, email FROM usuarios')
        users = cursor.fetchall()

        users_list = []
        for u in users:
            users_list.append({
                'id_usuario': u[0],
                'nome': u[1],
                'usuario': u[2],
                'email': u[3]
            })
        return jsonify(mensagem='Lista de Usuários', usuarios=users_list)
    except Exception as e:
        return jsonify(mensagem=f"Erro: {e}"), 500
    finally:
        cursor.close()



@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    nome = data.get('nome')
    usuario = data.get('usuario')
    senha = data.get('senha')
    email = data.get('email')

    if not nome or not usuario or not senha or not email:
        return jsonify({'error:': "Dados incompletos (nome, usuario, senha, email)"}), 400

    valida, msg = verificar_senha_forte(senha)

    if not valida:
        return jsonify({'error': 'Senha fraca', 'detalhes': msg}), 400

    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    try:
        cursor = con.cursor()

        cursor.execute('SELECT 1 FROM usuarios WHERE usuario = ? OR email = ?', (usuario, email))
        if cursor.fetchone():
            return jsonify({'error': "Usuário já existe!"}), 400

        cursor.execute('INSERT INTO usuarios (nome, usuario, senha, email) VALUES (?,?,?,?)', (nome, usuario, senha_hash, email))

        con.commit()

        return jsonify({
            'message': 'Usuário cadastrado com sucesso!',
            'usuario': {
                'nome': nome,
                'usuario': usuario,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify(mensagem=f'Erro: {e}'), 500
    finally:
        cursor.close()


@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):

    cursor = con.cursor()

    try:
        cursor.execute('SELECT nome, usuario, email, senha FROM usuarios WHERE id_usuario = ?', (id,))
        usuario_atual = cursor.fetchone()

        if not usuario_atual:
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        data = request.get_json()

        nome = data.get('nome', usuario_atual[0])
        usuario = data.get('usuario', usuario_atual[1])
        senha = data.get('senha', usuario_atual[3])
        email = data.get('email', usuario_atual[2])

        if senha:
            valida, msg = verificar_senha_forte(senha)
            if not valida:
                return jsonify({'error': 'Senha fraca', 'detalhes': msg}), 400
            senha_alterada = bcrypt.generate_password_hash(senha).decode('utf-8')

        else:
            senha_alterada = usuario_atual[0]

        cursor.execute('UPDATE usuarios SET nome = ?, usuario =?, senha = ?, email =? WHERE id_usuario = ?', (nome, usuario, senha_alterada, email, id))

        con.commit()
        return jsonify({
            "message": "Usuário atualizado com sucesso",
            'usuario': {
                'id_usuario': id,
                'nome': nome,
                'usuario': usuario,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify(mensagem=f'Erro: {e}'), 500
    finally:
        cursor.close()


@app.route('/apagar_usuario/<int:id>', methods=['DELETE'])
def apagar_usuario(id):
    cursor = con.cursor()
    try:

        cursor.execute('SELECT 1 FROM usuarios WHERE id_usuario = ?', (id,))
        usuario_existe = cursor.fetchone()

        if not usuario_existe:
            cursor.close()
            return jsonify({'error': 'Usuário não encontrado!'})


        cursor.execute('DELETE FROM usuarios WHERE id_usuario = ?', (id,))
        con.commit()

        return jsonify({"message": "Usuário apagado com sucesso!", 'id_usuario': id})
    except Exception as e:
        return jsonify({'error': f'Erro ao apagar: {e}'}), 500
    finally:
        cursor.close()




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email_login = data.get('email')
    senha_login = data.get('senha')

    if not email_login or not senha_login:
        return jsonify({'error': "Informe email e senha"}), 400

    cursor = con.cursor()

    try:
        cursor.execute('SELECT senha, nome, email FROM usuarios WHERE email = ?', (email_login,))
        dados_achados = cursor.fetchone()

        if not dados_achados:
            return jsonify({'error': "Email ou senha incorretos"}), 401

        senha_usuario = dados_achados[0]
        nome_usuario = dados_achados[1]
        email_usuario = dados_achados[2]

        if bcrypt.check_password_hash(senha_usuario, senha_login):
            return jsonify({'message': "Login realizado com sucesso!",
                            'usuario':{
                                "nome": nome_usuario,
                                "email": email_usuario
                            }}), 200

        else:
            return jsonify({'error': "Email ou senha incorretos"}), 401

    except Exception as e:
        return jsonify(mensagem=f'Erro no login: {e}'), 500
    finally:
        cursor.close()


@app.route('/relatorio_livro', methods=['GET'])
def relatorio_livros():
    cursor = con.cursor()
    try:
        cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM livros')
        dados = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)


        pdf.cell(200, 10, txt="Relatório de Livros", ln=1, align="C")
        pdf.ln(10)


        w_id = 15
        w_titulo = 95
        w_autor = 50
        w_ano = 30

        # Cabeçalho da Tabela
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(w_id, 10, "ID", 1, 0, 'C')
        pdf.cell(w_titulo, 10, "Título", 1, 0, 'C')
        pdf.cell(w_autor, 10, "Autor", 1, 0, 'C')
        pdf.cell(w_ano, 10, "Ano Publicação", 1, 1, 'C')


        pdf.set_font("Arial", size=10)
        for linha in dados:

            id_livro = str(linha[0])

            titulo = str(linha[1])

            if len(titulo) > 45:
                titulo = titulo[:42] + "..."

            autor = str(linha[2])

            if len(autor) > 25:
                autor = autor[:22] + "..."

            ano = str(linha[3])


            pdf.cell(w_id, 10, id_livro, 1, 0, 'C')
            pdf.cell(w_titulo, 10, titulo, 1, 0, 'L')
            pdf.cell(w_autor, 10, autor, 1, 0, 'L')
            pdf.cell(w_ano, 10, ano, 1, 1, 'C')

        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf')

    except Exception as e:
        return jsonify(mensagem=f"Erro: {e}"), 500
    finally:
        cursor.close()


@app.route('/relatorio_usuario', methods=['GET'])
def relatorio_usuarios():
    cursor = con.cursor()
    try:
        cursor.execute('SELECT id_usuario, nome, usuario, email FROM usuarios')
        dados = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título
        pdf.cell(200, 10, txt="Relatório de Usuários", ln=1, align="C")
        pdf.ln(10)


        w_id = 15
        w_nome = 55
        w_usuario = 40
        w_email = 80


        pdf.set_font("Arial", 'B', 10)
        pdf.cell(w_id, 10, "ID", 1, 0, 'C')
        pdf.cell(w_nome, 10, "Nome", 1, 0, 'C')
        pdf.cell(w_usuario, 10, "Usuário", 1, 0, 'C')
        pdf.cell(w_email, 10, "Email", 1, 1, 'C')


        pdf.set_font("Arial", size=10)
        for linha in dados:
            id_user = str(linha[0])


            nome = str(linha[1])
            if len(nome) > 25: nome = nome[:22] + "..."


            usuario = str(linha[2])
            if len(usuario) > 18: usuario = usuario[:15] + "..."


            email = str(linha[3])
            if len(email) > 38: email = email[:35] + "..."


            pdf.cell(w_id, 10, id_user, 1, 0, 'C')
            pdf.cell(w_nome, 10, nome, 1, 0, 'L')  # Alinhado à Esquerda (L)
            pdf.cell(w_usuario, 10, usuario, 1, 0, 'L')
            pdf.cell(w_email, 10, email, 1, 1, 'L')


        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf')

    except Exception as e:
        return jsonify(mensagem=f"Erro: {e}"), 500
    finally:
        cursor.close()


