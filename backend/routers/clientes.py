from fastapi import APIRouter, HTTPException, Query
from database import supabase

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("/")
def listar_clientes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = ""
):
    try:
        query = supabase.table("clientes").select("*")
        if search:
            # Buscar en nombre, telefono, direccion (case-insensitive)
            query = query.or_(
                f"nombre.ilike.%{search}%,telefono.ilike.%{search}%,direccion.ilike.%{search}%"
            )
        from_ = (page - 1) * limit
        to_ = from_ + limit - 1
        result = query.range(from_, to_).execute()
        clientes = result.data
        # Obtener el total de clientes (con o sin búsqueda)
        total_query = supabase.table("clientes").select("id")
        if search:
            total_query = total_query.or_(
                f"nombre.ilike.%{search}%,telefono.ilike.%{search}%,direccion.ilike.%{search}%"
            )
        total_result = total_query.execute()
        total = len(total_result.data)
        hay_mas = (from_ + limit) < total
        return {
            "clientes": clientes,
            "total": total,
            "hayMasPaginas": hay_mas
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}")
def obtener_cliente(id: int):
    try:
        result = supabase.table("clientes").select("*").eq("id", id).single().execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

@router.post("/crear")
def crear_cliente(cliente: dict):
    data = {
        "nombre": cliente.get("nombre"),
        "telefono": cliente.get("telefono"),
        "direccion": cliente.get("direccion"),
        "usuario_id": cliente.get("usuario_id")
    }
    try:
        result = supabase.table("clientes").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/editar")
def editar_cliente(cliente: dict):
    id_cliente = cliente.get("id")
    if not id_cliente:
        raise HTTPException(status_code=400, detail="ID requerido para editar")
    data = {
        "nombre": cliente.get("nombre"),
        "telefono": cliente.get("telefono"),
        "direccion": cliente.get("direccion"),
        "usuario_id": cliente.get("usuario_id")
    }
    try:
        result = supabase.table("clientes").update(data).eq("id", id_cliente).execute()
        return result.data[0] if result.data else {"mensaje": "Cliente actualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/eliminar/{id}")
def eliminar_cliente(id: int):
    try:
        result = supabase.table("clientes").delete().eq("id", id).execute()
        return {"mensaje": "Cliente eliminado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))