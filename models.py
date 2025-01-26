from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base  # Certifique-se de que não há dependências de volta ao `database.py`

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role")

class Resultado(Base):
    __tablename__ = "resultados_lotofacil"

    numero_concurso = Column(Integer, primary_key=True, index=True)
    data_sorteio = Column(Date, nullable=False)
    numero_1 = Column(Integer, nullable=False)
    numero_2 = Column(Integer, nullable=False)
    numero_3 = Column(Integer, nullable=False)
    numero_4 = Column(Integer, nullable=False)
    numero_5 = Column(Integer, nullable=False)
    numero_6 = Column(Integer, nullable=False)
    numero_7 = Column(Integer, nullable=False)
    numero_8 = Column(Integer, nullable=False)
    numero_9 = Column(Integer, nullable=False)
    numero_10 = Column(Integer, nullable=False)
    numero_11 = Column(Integer, nullable=False)
    numero_12 = Column(Integer, nullable=False)
    numero_13 = Column(Integer, nullable=False)
    numero_14 = Column(Integer, nullable=False)
    numero_15 = Column(Integer, nullable=False)
