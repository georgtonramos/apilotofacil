from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:senha123@localhost/loterias")

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from models import Role, User, Resultado

# Criar todas as tabelas no banco de dados
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
