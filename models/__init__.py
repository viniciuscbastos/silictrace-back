import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importação dos modelos para registo no catálogo do SQLAlchemy
from models.base import Base
from models.ativo import Ativo
from models.auditoria import AuditoriaCVE

# Garante a existência do diretório local para persistência do SQLite
db_path = "database/"
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Conexão com o banco de dados SQLite
db_url = f'sqlite:///{db_path}db.sqlite3'
engine = create_engine(db_url, echo=False)

# Configuração da sessão do SQLAlchemy para consultas e transações
Session = sessionmaker(bind=engine)

# Cria as tabelas 'ativos' e 'auditorias_cve' automaticamente no SQLite
Base.metadata.create_all(engine)