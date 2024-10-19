import hashlib
from flask import (
    Flask,
    redirect,
    request,
    jsonify,
    render_template,
    url_for,
    session,
)
from flask_caching import Cache
import psycopg2
from psycopg2 import sql
from datetime import datetime
import requests


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Chave secreta para criptografar sessões
cache = Cache(app, config={"CACHE_TYPE": "simple"})  # Configuração do Cache


# Configurações do banco de dados
DB_CONFIG = {
    "dbname": "pet_eletrica",
    "user": "postgres",
    "password": "2584",
    "host": "localhost",
    "port": "5432",
}


def get_db_connection():
    """
    Função para conectar ao banco de dados PostgreSQL
    Retorna um objeto connection da biblioteca psycopg2

    :return: Conexão com o banco de dados
    :rtype: psycopg2.extensions.connection
    """
    return psycopg2.connect(**DB_CONFIG)


@app.route("/", methods=["GET"])
def index():
    """
    Página principal do dashboard, acessível somente para usuários logados.
    Caso o usuário esteja logado, renderiza a página principal com o nome do usuário.
    Caso contrário, redireciona para a página de login.
    """
    if "user" in session:
        return render_template("dashboard.html")
    else:
        return render_template("login_e_cadastro.html")

@app.route("/<page>")
def render_page(page):
    """
    Função genérica para renderizar páginas.
    Caso o usuário esteja logado, renderiza a página especificada.
    Caso contrário, redireciona para a página de login.
    """
    if "user" in session:
        return render_template(page + ".html")
    else:
        return render_template("login_e_cadastro.html")

@app.route("/cadastrar_usuario", methods=["POST"])
def cadastrar_usuario():
    """
    Função para cadastrar um novo usuário no banco de dados.
    Recebe dados do formulário de cadastro via POST e insere um novo registro na tabela usuarios_painel.
    Verifica se o usuário já existe e retorna um erro caso positivo.
    Gera um hash da senha e salva na base.
    Salva o conteúdo da imagem de perfil como binário.
    Retorna uma resposta JSON com status e mensagem de erro caso ocorra algum problema.
    Caso contrário, salva o usuário na sessão e redireciona para a página principal.
    """
    foto_file = request.files.get("profile_picture")
    nome = request.form.get("name")
    email = request.form.get("email")
    senha = request.form.get("password")
    data_cadastro = datetime.now()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Verificar se o usuário já existe
        cur.execute("SELECT COUNT(*) FROM usuarios_painel WHERE email = %s", (email,))
        if cur.fetchone()[0] > 0:
            return jsonify({"status": "error", "message": "Usuário já cadastrado"})

        # Gerar hash da senha
        hashed_password = hashlib.sha256(senha.encode()).hexdigest()

        # Ler o conteúdo da imagem como binário
        foto_binaria = foto_file.read() if foto_file else None

        # Inserir novo usuário
        cur.execute(
            "INSERT INTO usuarios_painel (nome, email, senha, data_cadastro, imagem_perfil) VALUES (%s, %s, %s, %s, %s)",
            (nome, email, hashed_password, data_cadastro, foto_binaria),
        )
        conn.commit()
        session["user"] = email  # Salva o usuário na sessão
        return redirect(url_for("index"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()  # Certifique-se de fechar a conexão com o banco de dados

@app.route("/login", methods=["POST"])
def login():
    """Autentica um usuário e salva na sessão.

    Verifica se o email e senha informados são válidos e, caso sejam, salva o
    email na sessão e redireciona para a página principal.
    Retorna uma resposta JSON com status e mensagem de erro caso ocorra algum
    problema.
    """
    email = request.form.get("email")
    senha = request.form.get("password")
    hashed_password = hashlib.sha256(senha.encode()).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM usuarios_painel WHERE email = %s AND senha = %s",
            (email, hashed_password),
        )
        result = cur.fetchone()
        if result is None:
            return jsonify({"status": "error", "message": "Email ou senha inválidos"})
        else:
            session["user"] = email  # Salva o usuário na sessão
            cache.delete("get_profile_img")
            return redirect(url_for("index"))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()

@app.route("/logout")
def logout():
    """Remove o usuário da sessão e redireciona para a página de login.

    Essa rota é acessada quando o usuário clica no link de logout na barra de
    navegação. Se o usuário estiver logado (ou seja, se a sessão contiver o
    atributo "user"), remove o usuário da sessão e redireciona para a página
    principal. Caso contrário, redireciona para a página de login.
    """
    
    if "user" in session:
        session.pop("user", None)  # Remove o usuário da sessão
        cache.delete("get_profile_img")
        return render_template("login_e_cadastro.html")
    else:
        return render_template("login_e_cadastro.html")

@app.route("/contar_users", methods=["GET"])
def contar_users():
    """Conta o número de usuários cadastrados.

    Retorna uma resposta JSON com o status e a contagem de usuários. Caso
    o usuário não esteja logado, redireciona para a página de login.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM usuarios")
            result = cur.fetchone()
            return jsonify({"status": "success", "count": result[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/contar_itens", methods=["GET"])
def contar_itens():
    """Conta o número de itens únicos cadastrados.

    Retorna uma resposta JSON com o status e a contagem de itens. Caso
    o usuário não esteja logado, redireciona para a página de login.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(DISTINCT nome) FROM itens")
            result = cur.fetchone()
            return jsonify({"status": "success", "count": result[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/contar_emprestimos_ativos", methods=["GET"])
def contar_emprestimos_ativos():
    """Conta o número de empréstimos ativos.

    Retorna uma resposta JSON com o status e a contagem de empréstimos
    ativos. Caso o usuário não esteja logado, redireciona para a página
    de login.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM itens_historico
                WHERE data_devolucao IS NULL
                """
            )
            result = cur.fetchone()
            return jsonify({"status": "success", "count": result[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/contar_emprestimos_atrasados", methods=["GET"])
def contar_emprestimos_atrasados():
    """Conta o número de empréstimos atrasados.

    Retorna uma resposta JSON com o status e a contagem de empréstimos
    atrasados. Caso o usuário não esteja logado, redireciona para a página
    de login.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM itens_historico
                WHERE CURRENT_DATE > data_prevista_devolucao
                AND data_devolucao IS NULL
                """
            )

            result = cur.fetchone()
            return jsonify({"status": "success", "count": result[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_emprestimos_ativos", methods=["GET"])
@cache.cached(timeout=0, key_prefix="emprestimos_ativos_cache")
def get_emprestimos_ativos():
    """Retorna uma lista de empréstimos ativos.

    Retorna uma lista de dicionários, onde cada dicionário representa um
    empréstimo ativo. Caso o usuário não esteja logado, redireciona para a
    página de login.

    Os dicionários possuem as seguintes chaves:
        - emprestimo_id: o ID do empréstimo
        - usuario_nome: o nome do usuário que fez o empréstimo
        - item_nome: o nome do item emprestado
        - item_qntd: a quantidade do item emprestado
        - data_emprestimo: a data em que o empréstimo foi feito
        - data_prevista_devolucao: a data prevista para a devolução do item

    A resposta é cacheada por 0 segundos, portanto a lista de empréstimos
    ativos é atualizada a cada requisição.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT ih.id, u.nome AS usuario_nome, i.nome AS item_nome, ih.qntd, ih.data_emprestimo, ih.data_prevista_devolucao
                FROM itens_historico ih
                JOIN usuarios u ON ih.usuario_id = u.id
                JOIN itens i ON ih.item_id = i.id
                WHERE data_devolucao IS NULL
                """
            )
            emprestimos_ativos = cur.fetchall()
            return jsonify(
                [
                    {
                        "emprestimo_id": item[0],
                        "usuario_nome": item[1],
                        "item_nome": item[2],
                        "item_qntd": item[3],
                        "data_emprestimo": item[4].strftime("%d/%m/%Y"),
                        "data_prevista_devolucao": item[5].strftime("%d/%m/%Y"),
                    }
                    for item in emprestimos_ativos
                ]
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_emprestimos_atrasados", methods=["GET"])
@cache.cached(timeout=0, key_prefix="emprestimos_atrasados_cache")
def get_emprestimos_atrasados():
    """
    Retorna uma lista de empréstimos atrasados.

    Retorna uma lista de dicionários, onde cada dicionário representa um
    empréstimo atrasado. Caso o usuário não esteja logado, redireciona para a
    página de login.

    Os dicionários possuem as seguintes chaves:
        - usuario_nome: o nome do usuário associado ao empréstimo
        - item_nome: o nome do item emprestado
        - item_qntd: a quantidade do item emprestado
        - data_emprestimo: a data em que o item foi emprestado
        - dias_atraso: a quantidade de dias de atraso do empréstimo

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT u.nome AS usuario_nome, i.nome AS item_nome, ih.qntd, ih.data_emprestimo,
                (current_date - ih.data_prevista_devolucao) AS dias_atraso
                FROM itens_historico ih
                JOIN usuarios u ON ih.usuario_id = u.id
                JOIN itens i ON ih.item_id = i.id
                WHERE data_devolucao IS NULL
                AND current_date > (ih.data_prevista_devolucao)
                """
            )
            emprestimos_atrasados = cur.fetchall()
            return jsonify(
                [
                    {
                        "usuario_nome": item[0],
                        "item_nome": item[1],
                        "item_qntd": item[2],
                        "data_emprestimo": item[3].strftime("%d/%m/%Y"),
                        "dias_atraso": item[4].days,
                    }
                    for item in emprestimos_atrasados
                ]
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_historico_emprestimos", methods=["GET"])
def get_historico_emprestimos():
    """
    Retorna o histórico de empréstimos.

    A resposta é uma lista de dicionários, onde cada dicionário tem as seguintes chaves:
        - usuario_nome: nome do usuário que fez o empréstimo
        - item_nome: nome do item que foi emprestado
        - item_qntd: quantidade do item que foi emprestado
        - data_emprestimo: data em que o item foi emprestado
        - data_devolucao: data em que o item foi devolvido

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT u.nome AS usuario_nome, i.nome AS item_nome, ih.qntd, ih.data_emprestimo, ih.data_devolucao
                FROM itens_historico ih
                JOIN usuarios u ON ih.usuario_id = u.id
                JOIN itens i ON ih.item_id = i.id
                WHERE data_devolucao IS NOT NULL
                """
            )
            historico_emprestimos = cur.fetchall()
            return jsonify(
                [
                    {
                        "usuario_nome": item[0],
                        "item_nome": item[1],
                        "item_qntd": item[2],
                        "data_emprestimo": item[3].strftime("%d/%m/%Y"),
                        "data_devolucao": item[4].strftime("%d/%m/%Y"),
                    }
                    for item in historico_emprestimos
                ]
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/add_item", methods=["POST"])
def add_item():
    """
    Adiciona um novo item ao estoque.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se o item foi adicionado com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        item_name = request.form["item_name"]
        item_quantity = request.form["item_quantity"]
        item_location = request.form["item_location"]

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO itens (nome, estoque, localizacao) VALUES (%s, %s, %s)",
                (item_name, item_quantity, item_location),
            )
            conn.commit()
            cache.delete("produtos_cache")
            return jsonify(
                {"status": "success", "message": "Item adicionado com sucesso."}
            )
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/add_user", methods=["POST"])
def add_user():
    """
    Adiciona um novo usuário ao banco de dados.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se o usuário foi adicionado com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        cpf = request.form["cpf"]
        nome = request.form["nome"]
        curso = request.form["curso"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        url_validador = f"https://api.invertexto.com/v1/validator?token=15394|Zdb1z6WCCioetFrlm5NXYDQ2PpUiHiag&value={cpf}"
        response = requests.get(url_validador)
        if response.status_code == 200:
            data = response.json()  # Converte a resposta em JSON
            cpf_valido = data["valid"]
        if cpf_valido:
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                # Verificar se o CPF já está cadastrado
                cur.execute("SELECT cpf FROM usuarios WHERE cpf = %s", (cpf,))
                if cur.fetchone():
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Usuário já cadastrado com este CPF.",
                        }
                    )

                # Adicionar novo usuário
                cur.execute(
                    "INSERT INTO usuarios (cpf, nome, curso, email, telefone) VALUES (%s, %s, %s, %s, %s)",
                    (cpf, nome, curso, email, telefone),
                )
                conn.commit()
                cache.delete("get_usuarios_cache")

                return jsonify(
                    {"status": "success", "message": "Usuário adicionado com sucesso"}
                )
            except Exception as e:
                conn.rollback()
                return jsonify({"status": "error", "message": str(e)})
            finally:
                cur.close()
                conn.close()
        else:
            return jsonify({"status": "error", "message": "CPF Inválido!"})
    else:
        return render_template("login_e_cadastro.html")

@app.route("/edit_user", methods=["POST"])
def edit_user():
    """
    Atualiza um usuário existente no banco de dados.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se o usuário foi atualizado com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        user_id = request.form.get("user_id")
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        curso = request.form.get("curso")

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE usuarios
                SET nome = %s, cpf = %s, telefone = %s, curso = %s, email = %s
                WHERE id = %s;
            """,
                (nome, cpf, telefone, curso, email, user_id),
            )
            conn.commit()
            cur.close()
            conn.close()
            cache.delete("get_usuarios_cache")
            return jsonify(
                {"status": "success", "message": "Usuário atualizado com sucesso!"}
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_item", methods=["GET"])
def get_item():
    """
    Retorna o nome do item com o ID especificado.

    A resposta é um JSON com as seguintes chaves:
        - nome: O nome do item
        - status: "success" se o item foi encontrado, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        item_id = request.args.get("item_id")

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("SELECT nome FROM itens WHERE id = %s", (item_id,))
            item = cur.fetchone()

            if item:
                return jsonify({"nome": item[0]})
            else:
                return jsonify({"status": "error", "message": "Item não encontrado."})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_users", methods=["GET"])
@cache.cached(timeout=0, key_prefix="get_usuarios_cache")
def get_users():
    """
    Retorna a lista de usuários com base na busca realizada.

    A resposta é um JSON com os seguintes campos:
        - id: O ID do usuário
        - nome: O nome do usuário
        - cpf: O CPF do usuário
        - telefone: O telefone do usuário
        - curso: O curso do usuário
        - email: O e-mail do usuário

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        search = request.args.get("search", "")

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            query = sql.SQL(
                "SELECT * FROM usuarios WHERE nome ILIKE %s OR cpf ILIKE %s"
            )
            cur.execute(query, (f"%{search}%", f"%{search}%"))
            users = cur.fetchall()
            return jsonify(users)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_items", methods=["GET"])
def get_items():
    """
    Retorna a lista de itens com base na busca realizada.

    A resposta é um JSON com os seguintes campos:
        - id: O ID do item
        - nome: O nome do item
        - quantidade: A quantidade do item no estoque
        - localizacao: A localização do item no estoque

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        search = request.args.get("search", "")

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            query = sql.SQL("SELECT * FROM itens WHERE nome ILIKE %s")
            cur.execute(query, (f"%{search}%",))
            items = cur.fetchall()
            return jsonify(items)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/borrow_item", methods=["POST"])
def borrow_item():    
    """
    Função para realizar o empréstimo de um item.

    Esta função espera que seja passado o user_id, items_id e a quantidade de cada item
    e a data de devolução prevista.

    A resposta será um JSON com os seguintes campos:
        - status: O status da operação (success ou error)
        - message: A mensagem de erro ou sucesso

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        user_id = request.form["user_id"]
        items_id = request.form["items_id"].split(",")
        items_id = [int(item) for item in items_id]
        tamanho = len(items_id)
        DevolucaoPrevista = request.form["DevolucaoPrevista"]
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            i = 0
            while i < (len(items_id)):
                item_id = items_id[i]
                quantity_requested = items_id[i + 1]
                i += 2
                cur.execute("SELECT nome, estoque FROM itens WHERE id = %s", (item_id,))
                item_row = cur.fetchone()
                if item_row is None:
                    return jsonify(
                        {"status": "error", "message": "Item não encontrado."}
                    )

                quantity_available = item_row

                if quantity_available < quantity_requested:
                    return jsonify(
                        {
                            "status": "error",
                            "message": f"Quantidade solicitada ({quantity_requested}), do item de ID {item_id}, excede o estoque disponível ({quantity_available}).",
                        }
                    )

                # Verificar se o item já está emprestado para o usuário
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM itens_historico WHERE usuario_id = %s AND item_id = %s AND data_devolucao IS NULL
                    )
                    """,
                    (user_id, item_id),
                )
                if cur.fetchone()[0]:
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Item já está emprestado para este usuário.",
                        }
                    )
                # Atualizar a quantidade do item no estoque
                cur.execute(
                    "UPDATE itens SET estoque = estoque - %s WHERE id = %s",
                    (quantity_requested, item_id),
                )

                # Inserir histórico de empréstimo
                cur.execute(
                    """
                    INSERT INTO itens_historico (usuario_id, item_id, qntd, data_emprestimo, data_devolucao, data_prevista_devolucao)
                    VALUES (%s, %s, %s,%s, NULL, %s)
                    """,
                    (
                        user_id,
                        item_id,
                        quantity_requested,
                        datetime.now(),
                        DevolucaoPrevista,
                    ),
                )

            conn.commit()
            cache.delete("emprestimos_ativos_cache")

            if (tamanho) == 2:
                return jsonify(
                    {"status": "success", "message": "Item emprestado com sucesso"}
                )
            else:
                return jsonify(
                    {"status": "success", "message": "Itens emprestado com sucesso"}
                )
        except Exception as e:
            conn.rollback()
            print(f"Erro: {str(e)}")
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/return_item", methods=["POST"])
def return_item():
    """
    Processa a devolução de um item emprestado.

    A requisição deve conter o ID do empréstimo a ser devolvido. A função atualiza
    a data de devolução no histórico de itens e incrementa a quantidade do item
    de volta ao estoque.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se a devolução foi processada com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    Se o usuário não estiver na sessão, redireciona para a página de login.

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        emprestimo_id = request.form["emprestimo_id"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "UPDATE itens_historico SET data_devolucao=%s where id = %s",
                (datetime.now(), emprestimo_id),
            )
            cur.execute(
                "SELECT itens.id, itens_historico.qntd FROM itens_historico INNER JOIN itens ON itens_historico.item_id = itens.id WHERE itens_historico.id = %s",
                (emprestimo_id,),
            )
            item_id, item_qntd = cur.fetchone()
            cur.execute(
                "UPDATE itens SET estoque = estoque + %s WHERE id = %s",
                (item_qntd, item_id),
            )

            conn.commit()
            cache.delete("emprestimos_ativos_cache")
            cache.delete("emprestimos_atrasados_cache")
            return jsonify(
                {"status": "success", "message": "Item devolvido com sucesso"}
            )
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/edit_item", methods=["POST"])
def edit_item():
    """
    Processa a edição de um item.

    A requisição deve conter os seguintes campos:
        - item_id: O ID do item a ser editado
        - item_name: O novo nome do item
        - item_quantity: A nova quantidade do item
        - item_location: A nova localização do item

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se a edição foi processada com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    Se o usuário não estiver na sessão, redireciona para a página de login.

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        item_id = request.form["item_id"]
        item_name = request.form["item_name"]
        item_quantity = request.form["item_quantity"]
        item_location = request.form["item_location"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Verificar se o item existe
            cur.execute("SELECT * FROM itens WHERE id = %s", (item_id,))
            if not cur.fetchone():
                return jsonify({"status": "error", "message": "Item não encontrado."})

            # Atualizar o nome e a quantidade do item
            cur.execute(
                "UPDATE itens SET nome = %s, estoque = %s, localizacao = %s WHERE id = %s",
                (item_name, item_quantity, item_location, item_id),
            )
            conn.commit()
            cache.delete("produtos_cache")
            return jsonify(
                {"status": "success", "message": "Item atualizado com sucesso!"}
            )
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/delete_user", methods=["POST"])
def delete_user():
    """
    Deleta um usuário com base no seu ID.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se o usuário foi deletado com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """
    if "user" in session:
        user_id = request.form["user_id"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Verificar se o usuário existe
            cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            if not cur.fetchone():
                return jsonify(
                    {"status": "error", "message": "Usuário não encontrado."}
                )

            # Deletar o usuário
            cur.execute("DELETE FROM itens_historico WHERE usuario_id = %s", (user_id,))
            cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()
            cache.delete("get_usuarios_cache")
            return jsonify(
                {"status": "success", "message": "Usuário deletado com sucesso!"}
            )
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/delete_item", methods=["POST"])
def delete_item():
    """
    Deleta um item do estoque com base no ID do item.

    A resposta é um JSON com as seguintes chaves:
        - status: "success" se o item foi deletado com sucesso, "error" caso contrário
        - message: Uma mensagem de sucesso ou erro

    A resposta é cacheada por 0 segundos, sendo atualizada a cada requisição.
    """

    if "user" in session:
        item_id = request.form["item_id"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Verificar se o item existe
            cur.execute("SELECT * FROM itens WHERE id = %s", (item_id,))
            if not cur.fetchone():
                return jsonify({"status": "error", "message": "Item não encontrado."})

            # Deletar o item da tabela
            cur.execute("DELETE FROM itens WHERE id = %s", (item_id,))
            conn.commit()
            cache.delete("produtos_cache")
            return jsonify(
                {"status": "success", "message": "Item excluído com sucesso!"}
            )
        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

@app.route("/get_estoque", methods=["GET"])
def get_estoque():
    """
    Retorna o estoque do item com base no ID do item.

    A resposta é um JSON com a quantidade do item em estoque.

    A resposta é cacheada por 0 segundos, portanto a quantidade do item em estoque é atualizada a cada requisição.
    """
    if "user" in session:
        item_id = request.args.get("item_id")

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("SELECT estoque FROM itens WHERE id = %s", (item_id,))
            item_row = cur.fetchone()

            conn.commit()
            return jsonify(*item_row)
        except Exception as e:
            conn.rollback()
            print(f"Erro: {str(e)}")
            return jsonify({"status": "error", "message": str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return render_template("login_e_cadastro.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
