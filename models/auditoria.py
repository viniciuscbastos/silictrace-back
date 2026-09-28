from sqlalchemy import Column, Integer, String, Float, ForeignKey
from models.base import Base

# Tabela para salvar as vulnerabilidades vinculadas a cada ativo (relação 1:N)
class AuditoriaCVE(Base):
    __tablename__ = "auditorias_cve"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Chave estrangeira que aponta para o ativo auditado
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    
    cve_id = Column(String(50), nullable=False)         # Identificador da falha (ex: CVE-2023-20593)
    descricao = Column(String(500), nullable=False)     # Resumo da vulnerabilidade retornado pela API
    cvss_score = Column(Float, nullable=False, default=0.0)  # Severidade/impacto de 0.0 a 10.0

    def __init__(self, ativo_id: int, cve_id: str, descricao: str, cvss_score: float = 0.0):
        self.ativo_id = ativo_id
        self.cve_id = cve_id
        self.descricao = descricao
        self.cvss_score = cvss_score