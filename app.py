from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag

from models import Session
from models.ativo import Ativo
from models.auditoria import AuditoriaCVE
from services.cve_service import consultar_vulnerabilidades
from schemas.ativo import (
    AtivoSchema,
    AtivoUpdateSchema,
    AtivoBuscaSchema,
    AtivoViewSchema,
    ListaAtivosViewSchema,
)
from schemas.error import MensagemErroSchema

# Configuração da documentação OpenAPI e Swagger
info = Info(
    title="SilicTrace API",
    version="1.1.0",
    description="API de Gestão de Ativos Críticos de Hardware e Auditoria de Firmware/Microcódigo"
)
app = OpenAPI(__name__, info=info)
CORS(app)

# Tags de agrupamento das rotas na documentação
ativo_tag = Tag(name="Ativos de Hardware", description="Operações de CRUD e auditoria de inventário")
doc_tag = Tag(name="Documentação", description="Documentação interativa")


# Converte a instância do SQLAlchemy em dicionário para retorno da API
def serializar_ativo(ativo: Ativo) -> dict:
    return {
        "id": ativo.id,
        "tag_patrimonio": ativo.tag_patrimonio,
        "categoria": ativo.categoria,
        "fabricante": ativo.fabricante,
        "cpu": ativo.cpu,
        "gpu": ativo.gpu,
        "memoria_ram": ativo.memoria_ram,
        "armazenamento_primario": ativo.armazenamento_primario,
        "versao_bios": ativo.versao_bios,
        "versao_microcodigo": ativo.versao_microcodigo,
        "auditorias": getattr(ativo, "auditorias", [])
    }


# Rota raiz: redireciona para a interface do Swagger
@app.get('/', tags=[doc_tag], summary="Redirecionamento para documentação")
def home():
    return redirect('/openapi')


# POST: cadastra um novo ativo e consulta as vulnerabilidades iniciais no CIRCL
@app.post('/ativo', tags=[ativo_tag], responses={"200": AtivoViewSchema, "400": MensagemErroSchema, "500": MensagemErroSchema})
def criar_ativo(form: AtivoSchema):
    session = Session()
    try:
        # Evita duplicidade de tag de patrimônio
        if session.query(Ativo).filter(Ativo.tag_patrimonio == form.tag_patrimonio).first():
            return {"mensagem": f"Ativo com a tag {form.tag_patrimonio} já se encontra registado."}, 400

        novo_ativo = Ativo(
            tag_patrimonio=form.tag_patrimonio,
            categoria=form.categoria,
            fabricante=form.fabricante,
            cpu=form.cpu,
            gpu=form.gpu,
            memoria_ram=form.memoria_ram,
            armazenamento_primario=form.armazenamento_primario,
            versao_bios=form.versao_bios,
            versao_microcodigo=form.versao_microcodigo
        )
        session.add(novo_ativo)
        session.commit()
        session.refresh(novo_ativo)

        # Consulta a base do CIRCL e vincula as falhas encontradas ao ativo (1:N)
        cves = consultar_vulnerabilidades(novo_ativo.fabricante, novo_ativo.versao_microcodigo)
        for item in cves:
            auditoria = AuditoriaCVE(
                ativo_id=novo_ativo.id,
                cve_id=item.get("cve_id"),
                descricao=item.get("descricao"),
                cvss_score=float(item.get("cvss_score", 0.0)) if item.get("cvss_score") else 0.0
            )
            session.add(auditoria)
        session.commit()

        dados_retorno = serializar_ativo(novo_ativo)
        dados_retorno["auditorias"] = cves
        return dados_retorno, 200
    except Exception as e:
        session.rollback()
        return {"mensagem": f"Erro interno ao processar registo: {str(e)}"}, 500
    finally:
        session.close()


# GET: lista todos os ativos com suas respectivas vulnerabilidades cadastradas
@app.get('/ativos', tags=[ativo_tag], responses={"200": ListaAtivosViewSchema, "500": MensagemErroSchema})
def listar_ativos():
    session = Session()
    try:
        ativos = session.query(Ativo).order_by(Ativo.id.desc()).all()
        lista = []
        for a in ativos:
            item = serializar_ativo(a)
            # Busca as vulnerabilidades salvas para cada ativo
            auditorias_db = session.query(AuditoriaCVE).filter(AuditoriaCVE.ativo_id == a.id).all()
            item["auditorias"] = [
                {
                    "cve_id": aud.cve_id,
                    "descricao": aud.descricao,
                    "cvss_score": aud.cvss_score
                }
                for aud in auditorias_db
            ]
            lista.append(item)
        return {"ativos": lista}, 200
    except Exception as e:
        return {"mensagem": f"Erro ao recuperar ativos: {str(e)}"}, 500
    finally:
        session.close()


# PUT: atualiza a versão e reavalia as vulnerabilidades no CIRCL
@app.put('/ativo', tags=[ativo_tag], responses={"200": AtivoViewSchema, "404": MensagemErroSchema, "500": MensagemErroSchema})
def atualizar_ativo(form: AtivoUpdateSchema):
    session = Session()
    try:
        ativo = session.query(Ativo).filter(Ativo.tag_patrimonio == form.tag_patrimonio).first()
        if not ativo:
            return {"mensagem": f"Ativo com tag {form.tag_patrimonio} não encontrado."}, 404

        if form.nova_versao_bios:
            ativo.versao_bios = form.nova_versao_bios

        # Atualiza o microcódigo e consulta o CIRCL para verificar se a versão é segura
        if form.nova_versao_microcodigo:
            ativo.versao_microcodigo = form.nova_versao_microcodigo

            cves = consultar_vulnerabilidades(ativo.fabricante, form.nova_versao_microcodigo)

            # Limpa auditorias anteriores
            session.query(AuditoriaCVE).filter(AuditoriaCVE.ativo_id == ativo.id).delete()

            # Se a versão informada ainda estiver vulnerável, salva novamente no banco
            for item in cves:
                auditoria = AuditoriaCVE(
                    ativo_id=ativo.id,
                    cve_id=item.get("cve_id"),
                    descricao=item.get("descricao"),
                    cvss_score=float(item.get("cvss_score", 0.0)) if item.get("cvss_score") else 0.0
                )
                session.add(auditoria)

        session.commit()
        session.refresh(ativo)

        dados_retorno = serializar_ativo(ativo)
        auditorias_db = session.query(AuditoriaCVE).filter(AuditoriaCVE.ativo_id == ativo.id).all()
        dados_retorno["auditorias"] = [
            {
                "cve_id": aud.cve_id,
                "descricao": aud.descricao,
                "cvss_score": aud.cvss_score
            }
            for aud in auditorias_db
        ]
        return dados_retorno, 200
    except Exception as e:
        session.rollback()
        return {"mensagem": f"Erro ao atualizar ativo: {str(e)}"}, 500
    finally:
        session.close()


# DELETE: remove o ativo e faz a limpeza das auditorias vinculadas
@app.delete('/ativo', tags=[ativo_tag], responses={"200": MensagemErroSchema, "404": MensagemErroSchema, "500": MensagemErroSchema})
def remover_ativo(query: AtivoBuscaSchema):
    session = Session()
    try:
        ativo = session.query(Ativo).filter(Ativo.tag_patrimonio == query.tag_patrimonio).first()
        if not ativo:
            return {"mensagem": f"Ativo com tag {query.tag_patrimonio} não encontrado."}, 404

        # Remove as auditorias vinculadas antes de excluir o ativo
        session.query(AuditoriaCVE).filter(AuditoriaCVE.ativo_id == ativo.id).delete()
        session.delete(ativo)
        session.commit()
        return {"mensagem": f"Ativo {query.tag_patrimonio} removido com sucesso."}, 200
    except Exception as e:
        session.rollback()
        return {"mensagem": f"Erro ao remover ativo: {str(e)}"}, 500
    finally:
        session.close()


# Inicialização do servidor em modo desenvolvimento
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)