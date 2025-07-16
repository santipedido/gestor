from fastapi import APIRouter, HTTPException, Query, Body
from database import supabase
from schemas import Producto
# from supabase_py.lib.client import CountMethod

router = APIRouter(prefix="/productos", tags=["productos"])

@router.get("/")
def listar_productos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = ""
):
    try:
        query = supabase.table("productos").select("*")
        if search:
            query = query.ilike("nombre", f"%{search}%")
        from_ = (page - 1) * limit
        to_ = from_ + limit - 1
        result = query.range(from_, to_).execute()
        productos = result.data
        # Obtener el total de productos (con o sin búsqueda)
        total_query = supabase.table("productos").select("id")
        if search:
            total_query = total_query.ilike("nombre", f"%{search}%")
        total_result = total_query.execute()
        total = len(total_result.data)
        hay_mas = (from_ + limit) < total
        return {
            "productos": productos,
            "total": total,
            "hayMasPaginas": hay_mas
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}")
def obtener_producto(id: int):
    try:
        result = supabase.table("productos").select("*").eq("id", id).single().execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/crear")
def crear_producto(producto: Producto):
    if not producto.nombre or not producto.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio.")
    if producto.precio is None or producto.precio <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor a cero.")
    # Validar nombre único (case-insensitive)
    existe = supabase.table("productos").select("id").ilike("nombre", producto.nombre.strip()).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese nombre.")
    data = {
        "nombre": producto.nombre.strip(),
        "precio": producto.precio,
        "unidades_por_paca": producto.unidades_por_paca
    }
    try:
        result = supabase.table("productos").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/editar")
def editar_producto(producto: Producto):
    if not producto.id:
        raise HTTPException(status_code=400, detail="ID requerido para editar")
    if not producto.nombre or not producto.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio.")
    if producto.precio is None or producto.precio <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor a cero.")
    # Validar nombre único (case-insensitive, excluyendo el propio id)
    existe = supabase.table("productos").select("id").ilike("nombre", producto.nombre.strip()).execute()
    if existe.data and any(p['id'] != producto.id for p in existe.data):
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese nombre.")
    data = {
        "nombre": producto.nombre.strip(),
        "precio": producto.precio,
        "unidades_por_paca": producto.unidades_por_paca
    }
    try:
        result = supabase.table("productos").update(data).eq("id", producto.id).execute()
        return result.data[0] if result.data else {"mensaje": "Producto actualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/eliminar/{id}")
def eliminar_producto(id: int):
    try:
        supabase.table("productos").delete().eq("id", id).execute()
        return {"mensaje": "Producto eliminado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/importar")
def importar_productos(payload: dict = Body(...)):
    productos = payload.get("productos", [])
    if not productos or not isinstance(productos, list):
        raise HTTPException(status_code=400, detail="Debes enviar una lista de productos.")
    errores = []
    insertados = 0
    for idx, prod in enumerate(productos):
        nombre = prod.get("nombre", "").strip()
        precio = prod.get("precio")
        unidades_por_paca = prod.get("unidades_por_paca")
        if not nombre:
            errores.append(f"Fila {idx+2}: El nombre es obligatorio.")
            continue
        if precio is None or not isinstance(precio, (int, float)) or precio <= 0:
            errores.append(f"Fila {idx+2}: El precio debe ser mayor a cero.")
            continue
        # Validar nombre único (case-insensitive)
        existe = supabase.table("productos").select("id").ilike("nombre", nombre).execute()
        if existe.data:
            errores.append(f"Fila {idx+2}: Ya existe un producto con el nombre '{nombre}'.")
            continue
        data = {"nombre": nombre, "precio": precio, "unidades_por_paca": unidades_por_paca}
        try:
            supabase.table("productos").insert(data).execute()
            insertados += 1
        except Exception as e:
            errores.append(f"Fila {idx+2}: Error al insertar: {str(e)}")
    if errores:
        raise HTTPException(status_code=400, detail="Errores en la importación: " + "; ".join(errores))
    return {"mensaje": f"{insertados} productos importados exitosamente."}