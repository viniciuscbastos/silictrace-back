from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from models.base import Base

class Ativo(Base):
    """
    Representa um ativo crítico de hardware inventariado no sistema.
    Armazena especificações físicas e versões de firmware para auditoria de vulnerabilidades.
    """
    __tablename__ = "ativos"

    # Identificador primário interno
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identificação e classificação do equipamento
    tag_patrimonio = Column(String(50), unique=True, nullable=False)
    categoria = Column(String(50), nullable=False)        # 'Workstation' ou 'Servidor'
    fabricante = Column(String(20), nullable=False)       # 'AMD' ou 'Intel'

    # Especificações de hardware
    cpu = Column(String(100), nullable=False)
    gpu = Column(String(100), nullable=False)
    memoria_ram = Column(Integer, nullable=False)         # Em Gigabytes (GB)
    armazenamento_primario = Column(String(100), nullable=False)

    # Camada de firmware e microcódigo (auditada contra CVEs)
    versao_bios = Column(String(50), nullable=False)       # Ex.: 'ASUS 1402' ou 'Dell 2.4.1'
    versao_microcodigo = Column(String(50), nullable=False)# Ex.: AGESA ('1.2.0.2') ou MCU Intel ('0x12B')

    # Data de registo no inventário
    data_insercao = Column(DateTime, default=datetime.utcnow)