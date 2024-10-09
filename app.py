from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2 import sql
from datetime import datetime
import requests

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "dbname": "pet_eletrica",
    "user": "postgres",
    "password": "2584",
    "host": "localhost",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/usuarios")
def usuarios():
    return render_template("usuarios.html")


@app.route("/produtos")
def produtos():
    return render_template("produtos.html")


@app.route("/emprestimos")
def emprestimos():
    return render_template("emprestimos.html")


@app.route("/contar_users", methods=["GET"])
def contar_users():
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


@app.route("/contar_itens", methods=["GET"])
def contar_itens():
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


@app.route("/contar_emprestimos_ativos", methods=["GET"])
def contar_emprestimos_ativos():
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


@app.route("/contar_emprestimos_atrasados", methods=["GET"])
def contar_emprestimos_atrasados():
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


@app.route("/get_emprestimos_ativos", methods=["GET"])
def get_emprestimos_ativos():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT u.nome AS usuario_nome, i.nome AS item_nome, ih.qntd, ih.data_emprestimo, ih.data_prevista_devolucao
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
                    "usuario_nome": item[0],
                    "item_nome": item[1],
                    "item_qntd": item[2],
                    "data_emprestimo": item[3].strftime("%d/%m/%Y"),
                    "data_prevista_devolucao": item[4].strftime("%d/%m/%Y"),
                }
                for item in emprestimos_ativos
            ]
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_emprestimos_atrasados", methods=["GET"])
def get_emprestimos_atrasados():
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


@app.route("/get_historico_emprestimos", methods=["GET"])
def get_historico_emprestimos():
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


@app.route("/add_item", methods=["POST"])
def add_item():
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
        return jsonify({"status": "success", "message": "Item adicionado com sucesso."})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_delayeds", methods=["GET"])
def get_delayeds():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Definindo a consulta SQL
        query = """
            SELECT u.nome AS usuario_nome, i.nome AS item_nome, 
                   DATE_TRUNC('day', NOW()) - DATE_TRUNC('day', ih.data_prevista_devolucao) AS atraso
            FROM itens_historico ih
            INNER JOIN usuarios u ON ih.usuario_id = u.id
            INNER JOIN itens i ON ih.item_id = i.id
            WHERE ih.data_devolucao IS NULL 
              AND ih.data_prevista_devolucao < CURRENT_DATE;
        """
        cur.execute(query)
        atrasados = cur.fetchall()

        # Construindo a lista de dicionários para retorno JSON
        resultados = []
        for atraso in atrasados:
            resultado = {
                "nome_pessoa": atraso[0],  # Correção do índice para nome do usuário
                "nome_item": atraso[1],  # Correção do índice para nome do item
                "tempo_atraso": str(atraso[2]).split()[
                    0
                ],  # Extrai apenas o número de dias
            }
            resultados.append(resultado)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route("/add_user", methods=["POST"])
def add_user():
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
        if cpf and nome and curso and telefone:
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
            return jsonify({"status": "error", "message": "Preencha Todos os Campos!"})
    else:
        return jsonify({"status": "error", "message": "CPF Inválido!"})


@app.route("/edit_user", methods=["POST"])
def edit_user():
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
        return jsonify(
            {"status": "success", "message": "Usuário atualizado com sucesso!"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/get_item", methods=["GET"])
def get_item():
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


@app.route("/get_phone_by_name", methods=["GET"])
def get_phone_by_name():
    user_name = request.args.get("user_name")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Buscar o telefone do usuário pelo nome
        cur.execute("SELECT telefone FROM usuarios WHERE nome ILIKE %s", (user_name,))
        telefone = cur.fetchone()
        if telefone:
            # telefone é uma tupla, então pegue o primeiro item
            telefone = telefone[0]
            return jsonify({"telefone": telefone})
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_user", methods=["GET"])
def get_user():
    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Buscar as informações do usuário pelo ID
        cur.execute(
            "SELECT nome, cpf, curso, telefone, email FROM usuarios WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()

        if user:
            user_data = {
                "nome": user[0],
                "cpf": user[1],
                "curso": user[2],
                "telefone": user[3],
                "email": user[4],
            }
            return jsonify(user_data)
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_users", methods=["GET"])
def get_users():
    search = request.args.get("search", "")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = sql.SQL("SELECT * FROM usuarios WHERE nome ILIKE %s OR cpf ILIKE %s")
        cur.execute(query, (f"%{search}%", f"%{search}%"))
        users = cur.fetchall()
        return jsonify(users)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_items", methods=["GET"])
def get_items():
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


@app.route("/get_user_items", methods=["GET"])
def get_user_items():
    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Buscar itens emprestados e a data prevista de devolução
        cur.execute(
            """
            SELECT i.nome, ih.data_prevista_devolucao 
            FROM itens_historico ih
            JOIN itens i ON ih.item_id = i.id
            WHERE ih.usuario_id = %s AND ih.data_devolucao IS NULL
            """,
            (user_id,),
        )
        itens_emprestados = cur.fetchall()

        # Buscar histórico de itens
        cur.execute(
            """
            SELECT i.nome, ih.data_emprestimo, ih.data_devolucao, ih.data_prevista_devolucao
            FROM itens_historico ih
            JOIN itens i ON ih.item_id = i.id
            WHERE ih.usuario_id = %s
            ORDER BY ih.data_emprestimo DESC
            """,
            (user_id,),
        )
        historico_itens = cur.fetchall()

        return jsonify(
            {
                "itensEmprestados": [
                    {
                        "nome": item[0],
                        "dataPrevistaDevolucao": item[1],
                    }
                    for item in itens_emprestados
                ],
                "historicoItens": [
                    {
                        "nome": item[0],
                        "dataEmprestimo": item[1],
                        "dataDevolucao": item[2],
                        "dataPrevistaDevolucao": item[3],
                    }
                    for item in historico_itens
                ],
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/borrow_item", methods=["POST"])
def borrow_item():
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
                return jsonify({"status": "error", "message": "Item não encontrado."})

            item_name, quantity_available = item_row

            if quantity_available < quantity_requested:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Quantidade solicitada ({quantity_requested}), do item de ID {item_id}, excede o estoque disponível ({quantity_available}).",
                    }
                )

            # Verificar se o item já está emprestado para o usuário
            cur.execute(
                "SELECT itens_emprestados FROM usuarios WHERE id = %s", (user_id,)
            )
            itens_emprestados = cur.fetchone()[0] or []

            if any(item_name in item for item in itens_emprestados):
                return jsonify(
                    {
                        "status": "error",
                        "message": "Item já está emprestado para este usuário.",
                    }
                )

            # Atualizar o registro do usuário
            cur.execute(
                """
                UPDATE usuarios 
                SET itens_emprestados = array_append(itens_emprestados, %s)
                WHERE id = %s
                """,
                (f"{item_name}:{quantity_requested}", user_id),
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


@app.route("/update_stock", methods=["POST"])
def update_item_stock():
    item_id = request.form["item_id"]
    new_stock = int(request.form["new_stock"])

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE itens SET estoque = %s WHERE id = %s", (new_stock, item_id))
        conn.commit()
        return jsonify(
            {"status": "success", "message": "Estoque atualizado com sucesso."}
        )
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/return_item", methods=["POST"])
def return_item():
    user_id = request.form["user_id"]
    item_name = request.form["item_name"]

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Verificar se o item está emprestado
        cur.execute("SELECT itens_emprestados FROM usuarios WHERE id = %s", (user_id,))
        itens_emprestados_row = cur.fetchone()
        itens_emprestados = itens_emprestados_row[0] if itens_emprestados_row[0] else []

        # Encontrar o item no array de itens emprestados
        item_to_return = None
        for item in itens_emprestados:
            if item.startswith(item_name + ":"):
                item_to_return = item
                break

        if item_to_return is None:
            return jsonify(
                {
                    "status": "error",
                    "message": "Item não está emprestado para este usuário.",
                }
            )

        # Remover item do array de itens emprestados
        itens_emprestados.remove(item_to_return)
        cur.execute(
            "UPDATE usuarios SET itens_emprestados = %s WHERE id = %s",
            (itens_emprestados, user_id),
        )

        # Obter o ID do item e a quantidade emprestada
        item_quantity = int(item_to_return.split(":")[1])
        cur.execute("SELECT id FROM itens WHERE nome = %s", (item_name,))
        item_id_row = cur.fetchone()
        if item_id_row is None:
            return jsonify(
                {
                    "status": "error",
                    "message": "Item não encontrado.",
                }
            )
        item_id = item_id_row[0]

        # Atualizar a quantidade do item no estoque
        cur.execute(
            "UPDATE itens SET estoque = estoque + %s WHERE id = %s",
            (item_quantity, item_id),
        )

        # Atualizar o histórico com a data de devolução
        cur.execute(
            """
            UPDATE itens_historico 
            SET data_devolucao = %s 
            WHERE usuario_id = %s 
              AND item_id = %s 
              AND data_devolucao IS NULL
            """,
            (datetime.now(), user_id, item_id),
        )

        conn.commit()
        return jsonify({"status": "success", "message": "Item devolvido com sucesso"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/edit_item", methods=["POST"])
def edit_item():
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
        return jsonify({"status": "success", "message": "Item atualizado com sucesso!"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/delete_item", methods=["POST"])
def delete_item():
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
        return jsonify({"status": "success", "message": "Item excluído com sucesso!"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_item_qtd", methods=["GET"])
def get_item_qtd():
    userId = request.args.get("userId")
    item_id = request.args.get("item_id")
    quantity = int(request.args.get("quantity"))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT nome, estoque FROM itens WHERE id = %s", (item_id,))
        item_row = cur.fetchone()

        item_name, quantity_available = item_row

        if quantity_available < quantity:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Quantidade solicitada ({quantity}), do item de ID {item_id}, excede o estoque disponível ({quantity_available}).",
                }
            )

        # Verificar se o item já está emprestado para o usuário
        cur.execute("SELECT itens_emprestados FROM usuarios WHERE id = %s", (userId,))
        itens_emprestados = cur.fetchone()[0] or []

        if any(item_name in item for item in itens_emprestados):
            return jsonify(
                {
                    "status": "error",
                    "message": "Item já está emprestado para este usuário.",
                }
            )

        conn.commit()
        return jsonify({"status": "success", "message": "Item adicionado a lista!"})
    except Exception as e:
        conn.rollback()
        print(f"Erro: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()
        conn.close()


@app.route("/get_estoque", methods=["GET"])
def get_estoque():
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


if __name__ == "__main__":
    app.run(debug=True)
