from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role, Resultado
from schemas import User as UserSchema, Resultado as ResultadoSchema
from typing import List, Optional
import logging
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import bcrypt

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não está definido nas variáveis de ambiente.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Funções auxiliares para autenticação JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Dependência para verificar o token
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token")), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

# Dependência para verificar a função (role)
def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer função: {required_role}"
            )
        return current_user
    return role_dependency

# Inicializar o FastAPI
app = FastAPI()

@app.post("/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user and verify_password(form_data.password, user.password):
        logging.info(f"Autenticação bem-sucedida para o usuário: {form_data.username}")
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        logging.warning(f"Falha na autenticação para o usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/resultados", response_model=List[ResultadoSchema])
def listar_resultados(db: Session = Depends(get_db)):
    resultados = db.query(Resultado).order_by(Resultado.numero_concurso.desc()).all()
    return [
        ResultadoSchema(
            numero_concurso=res.numero_concurso,
            data_sorteio=res.data_sorteio.strftime("%Y-%m-%d"),
            numeros_sorteados=[
                res.numero_1, res.numero_2, res.numero_3, res.numero_4, res.numero_5,
                res.numero_6, res.numero_7, res.numero_8, res.numero_9, res.numero_10,
                res.numero_11, res.numero_12, res.numero_13, res.numero_14, res.numero_15
            ],
        )
        for res in resultados
    ]

@app.get("/resultados/{numero_concurso}", response_model=Optional[ResultadoSchema])
def listar_resultado_por_concurso(
    numero_concurso: int,
    current_user: User = Depends(require_role("Viewer")),
    db: Session = Depends(get_db)):
    resultado = db.query(Resultado).filter(Resultado.numero_concurso == numero_concurso).first()
    if resultado:
        logging.info(f"[API] Usuário {current_user.username} acessou /resultados/{numero_concurso} e encontrou: {resultado}")
        return ResultadoSchema(
            numero_concurso=resultado.numero_concurso,
            data_sorteio=resultado.data_sorteio.strftime("%Y-%m-%d"),
            numeros_sorteados=[
                resultado.numero_1, resultado.numero_2, resultado.numero_3, resultado.numero_4,
                resultado.numero_5, resultado.numero_6, resultado.numero_7, resultado.numero_8,
                resultado.numero_9, resultado.numero_10, resultado.numero_11, resultado.numero_12,
                resultado.numero_13, resultado.numero_14, resultado.numero_15
            ]
        )
    else:
        logging.warning(f"[API] Usuário {current_user.username} acessou /resultados/{numero_concurso} e não encontrou resultados.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado não encontrado.")
