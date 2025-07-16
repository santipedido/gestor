from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.clientes import router as clientes_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes_router)

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend funcionando!"}

# Puedes agregar tus rutas aquí