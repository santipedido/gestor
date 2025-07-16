from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.clientes import router as clientes_router
from routers.productos import router as productos_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sensational-alpaca-3c0c39.netlify.app/"],  # Permitir cualquier origen para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes_router)
app.include_router(productos_router)

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend funcionando!"}

# Puedes agregar tus rutas aquí
