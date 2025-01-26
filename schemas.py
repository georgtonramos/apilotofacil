from pydantic import BaseModel
from typing import List, Optional

# Modelo para funções (roles)
class RoleBase(BaseModel):
    name: str

class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True

# Modelo para usuários
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role_id: int

class User(UserBase):
    id: int
    role: Role

    class Config:
        orm_mode = True

# Modelo para resultados da Lotofácil
class Resultado(BaseModel):
    numero_concurso: int
    data_sorteio: str
    numeros_sorteados: List[int]

    class Config:
        orm_mode = True
