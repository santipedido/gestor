from fastapi import APIRouter, HTTPException
from database import supabase
from schemas import PedidoCreate
from typing import Optional

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.get("/")
def listar_pedidos(estado: Optional[str] = None):
    try:
        # Construir query base
        query = supabase.table("pedidos").select("*").order("fecha", desc=True).limit(10)
        
        # Aplicar filtro por estado si se proporciona
        if estado:
            if estado not in ["pendiente", "en proceso"]:
                raise HTTPException(status_code=400, detail="Estado debe ser 'pendiente' o 'en proceso'")
            query = query.eq("estado", estado)
        
        result = query.execute()
        pedidos = result.data
        
        # Obtener información del cliente para cada pedido
        for pedido in pedidos:
            if pedido.get("cliente_id"):
                cliente = supabase.table("clientes").select("nombre, telefono").eq("id", pedido["cliente_id"]).single().execute()
                if cliente.data:
                    pedido["cliente"] = cliente.data
        
        return {
            "pedidos": pedidos,
            "total": len(pedidos)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/crear")
def crear_pedido(pedido: PedidoCreate):
    # 1. Crear el pedido
    pedido_data = {
        "cliente_id": pedido.cliente_id,
        # fecha y estado se asignan por defecto en la base de datos
    }
    pedido_result = supabase.table("pedidos").insert(pedido_data).execute()
    if not pedido_result.data:
        raise HTTPException(status_code=400, detail="No se pudo crear el pedido")
    pedido_id = pedido_result.data[0]["id"]

    # 2. Agregar productos al pedido
    productos_a_insertar = []
    for prod in pedido.productos:
        # Obtener info del producto para validar tipo
        producto_db = supabase.table("productos").select("precio, unidades_por_paca").eq("id", prod.producto_id).single().execute().data
        if not producto_db:
            raise HTTPException(status_code=404, detail=f"Producto {prod.producto_id} no encontrado")
        # Validar tipo
        if prod.tipo == "paca":
            if not producto_db["unidades_por_paca"] or producto_db["unidades_por_paca"] <= 0:
                raise HTTPException(status_code=400, detail=f"El producto {prod.producto_id} no se vende por paca")
            precio_unitario = float(producto_db["precio"]) * int(producto_db["unidades_por_paca"])
        elif prod.tipo == "unidad":
            precio_unitario = float(producto_db["precio"])
        else:
            raise HTTPException(status_code=400, detail="Tipo inválido (debe ser 'unidad' o 'paca')")
        productos_a_insertar.append({
            "pedido_id": pedido_id,
            "producto_id": prod.producto_id,
            "tipo": prod.tipo,
            "cantidad": prod.cantidad,
            "precio_unitario": precio_unitario
        })
    # Insertar todos los productos del pedido
    if productos_a_insertar:
        supabase.table("pedido_productos").insert(productos_a_insertar).execute()

    return {"mensaje": "Pedido creado correctamente", "pedido_id": pedido_id}