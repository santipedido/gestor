# Proyecto Gestor de Pedidos

Estructura completa con backend (FastAPI) y frontend (Vue 3 con Vite).

## Instrucciones

### Backend
```bash
cd backend
python -m venv env
source env/bin/activate  # o env\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Variables de entorno
- Copiar `.env.example` como `.env`
- Llenar valores de Supabase
