from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from BarberTime.adapters import orm, repository
from BarberTime.service_layer import services

app = Flask(__name__)

DEFAULT_DB_URI = "sqlite:///barbertime.db"
engine = create_engine(DEFAULT_DB_URI)
orm.start_mappers()
orm.metadata.create_all(engine)
get_session = sessionmaker(bind=engine)

def get_repo(session):
    return repository.SqlAlchemyBarbeiroRepository(session)

def get_atendimento_repo(session):
    return repository.SqlAlchemyAtendimentoRepository(session)

def get_comissao_repo(session):
    return repository.SqlAlchemyComissaoRepository(session)

@app.route("/barbeiros", methods=["POST"])
def post_barbeiro():
    session = get_session()
    repo = get_repo(session)
    data = request.get_json() or {}
    try:
        resultado = services.cadastrar_barbeiro(
            id=data["id"],
            nome=data["nome"],
            horario_inicio=data.get("horario_inicio", "08:00"),
            horario_fim=data.get("horario_fim", "18:00"),
            dias_trabalho=data.get("dias_trabalho", "0,1,2,3,4,5"),
            repo=repo,
            session=session,
        )
        return jsonify(resultado), 201
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatorio ausente: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        session.close()

@app.route("/barbeiros", methods=["GET"])
def get_barbeiros():
    session = get_session()
    repo = get_repo(session)
    try:
        resultado = services.listar_barbeiros(repo=repo)
        return jsonify(resultado), 200
    finally:
        session.close()

@app.route("/barbeiros/<int:barbeiro_id>", methods=["GET"])
def get_barbeiro_by_id(barbeiro_id):
    session = get_session()
    repo = get_repo(session)
    try:
        resultado = services.consultar_barbeiro(barbeiro_id=barbeiro_id, repo=repo)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    finally:
        session.close()

@app.route("/barbeiros/<int:barbeiro_id>/expediente", methods=["PUT"])
def put_expediente(barbeiro_id):
    session = get_session()
    repo = get_repo(session)
    data = request.get_json() or {}
    try:
        resultado = services.atualizar_expediente(
            barbeiro_id=barbeiro_id,
            novo_inicio=data["horario_inicio"],
            novo_fim=data["horario_fim"],
            repo=repo,
            session=session,
        )
        return jsonify(resultado), 200
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatorio ausente: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        session.close()

@app.route("/barbeiros/<int:barbeiro_id>/validar_horario", methods=["POST"])
def post_validar_horario(barbeiro_id):
    session = get_session()
    repo = get_repo(session)
    data = request.get_json() or {}
    try:
        resultado = services.validar_horario_atendimento(
            barbeiro_id=barbeiro_id,
            data_hora=data["data_hora"],
            duracao_minutos=data.get("duracao", 0),
            repo=repo,
        )
        return jsonify(resultado), 200
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatorio ausente: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"valido": False, "erro": str(e)}), 400
    finally:
        session.close()

@app.route("/atendimentos", methods=["POST"])
def post_atendimento():
    session = get_session()
    atendimento_repo = get_atendimento_repo(session)
    barbeiro_repo = get_repo(session)
    data = request.get_json() or {}
    try:
        resultado = services.registrar_atendimento(
            atendimento_id=data["id"],
            barbeiro_id=data["barbeiro_id"],
            servico=data["servico"],
            data_hora=data["data_hora"],
            atendimento_repo=atendimento_repo,
            barbeiro_repo=barbeiro_repo,
            session=session,
        )
        return jsonify(resultado), 201
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatorio ausente: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        session.close()

@app.route("/atendimentos/<int:atendimento_id>", methods=["GET"])
def get_atendimento(atendimento_id):
    session = get_session()
    atendimento_repo = get_atendimento_repo(session)
    try:
        resultado = services.consultar_atendimento(
            atendimento_id=atendimento_id, repo=atendimento_repo
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    finally:
        session.close()

@app.route("/atendimentos/<int:atendimento_id>/concluir", methods=["POST"])
def post_concluir_atendimento(atendimento_id):
    session = get_session()
    atendimento_repo = get_atendimento_repo(session)
    try:
        resultado = services.concluir_atendimento(
            atendimento_id=atendimento_id,
            atendimento_repo=atendimento_repo,
            session=session,
        )
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        session.close()

@app.route("/comissoes", methods=["POST"])
def post_comissao():
    session = get_session()
    atendimento_repo = get_atendimento_repo(session)
    comissao_repo = get_comissao_repo(session)
    data = request.get_json() or {}
    try:
        resultado = services.gerar_comissao(
            comissao_id=data["id"],
            atendimento_id=data["atendimento_id"],
            percentual=data.get("percentual"),
            atendimento_repo=atendimento_repo,
            comissao_repo=comissao_repo,
            session=session,
        )
        return jsonify(resultado), 201
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatorio ausente: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        session.close()

@app.route("/comissoes", methods=["GET"])
def get_comissoes():
    session = get_session()
    comissao_repo = get_comissao_repo(session)
    try:
        resultado = services.listar_comissoes(repo=comissao_repo)
        return jsonify(resultado), 200
    finally:
        session.close()

@app.route("/comissoes/<int:comissao_id>", methods=["GET"])
def get_comissao_by_id(comissao_id):
    session = get_session()
    comissao_repo = get_comissao_repo(session)
    try:
        resultado = services.consultar_comissao(comissao_id=comissao_id, repo=comissao_repo)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    finally:
        session.close()

@app.route("/barbeiros/<int:barbeiro_id>/comissoes", methods=["GET"])
def get_comissoes_do_barbeiro(barbeiro_id):
    session = get_session()
    comissao_repo = get_comissao_repo(session)
    try:
        resultado = services.listar_comissoes_por_barbeiro(
            barbeiro_id=barbeiro_id, repo=comissao_repo
        )
        return jsonify(resultado), 200
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
