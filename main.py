from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

class IngresoBase(BaseModel):
    documentoingreso:str
    nombrepersona:str

# codigo para actualizar datos
class IngresoBase2(BaseModel):
    idregistro:int
    documentoingreso:str
    nombrepersona:str    

    # activar interaccion con base de datos
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()   

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/registro/", status_code=status.HTTP_201_CREATED)
async def crear_registro(registro:IngresoBase, db:db_dependency):
    db_registro = models.Ingreso(**registro.dict())
    db.add(db_registro)
    db.commit()
    return "Registro realizado exitosamente"

@app.get("/listarregistros/", status_code=status.HTTP_200_OK)
async def consultar_registros(db:db_dependency):
    registros = db.query(models.Ingreso).all()
    return registros

@app.get("/consultaregistro/{documento_ingreso}", status_code=status.HTTP_200_OK)
async def consultar_registro_por_documento(documento_ingreso, db:db_dependency):
    registro = db.query(models.Ingreso).filter(models.Ingreso.documentoingreso==documento_ingreso).first()
    if registro is None:
        HTTPException(status_code=404, detail="Registro no encontrado")
    return registro

@app.delete("/borrarregistro/{id_registro}", status_code=status.HTTP_200_OK)
async def borrar_registro(id_registro, db:db_dependency):
    registroborrar = db.query(models.Ingreso).filter(models.Ingreso.idregistro==id_registro).first()
    if registroborrar is None:
        HTTPException(status_code=404, detail="Registro no encontrado, no se pudo eliminar")
    db.delete(registroborrar)
    db.commit()
    return "Registro eliminado exitosamente"

@app.post("/actualizarregistro/", status_code=status.HTTP_200_OK)
async def actualizar_registro (registro:IngresoBase2, db:db_dependency):
    registroactualizar = db.query(models.Ingreso).filter(models.Ingreso.idregistro==registro.idregistro).first()
    if registroactualizar is None:
        HTTPException(status_code=404, detail="No se encontro registro para la consulta")
    registroactualizar.documentoingreso = registro.documentoingreso
    registroactualizar.nombrepersona = registro.nombrepersona
    db.commit()
    return "Registro actualizado exitosamente"