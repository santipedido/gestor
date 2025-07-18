from fastapi import APIRouter, HTTPException
from database import supabase
from schemas import PedidoCreate
from typing import Optional
from datetime import datetime
import os
import requests

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

def armar_mensaje_whatsapp(cliente_nombre, cliente_telefono, productos, total, fecha, estado):
    mensaje = f"""📝 *Nuevo pedido recibido*\n\n👤 *Cliente:* {cliente_nombre}\n📞 *Teléfono:* {cliente_telefono}\n\n📦 *Productos:*\n"""
    for prod in productos:
        if prod['tipo'] == 'paca':
            tipo = f"Paca de {prod['unidades_por_paca']} und"
            precio = prod['precio_unitario']
        else:
            tipo = "Unidad"
            precio = prod['precio_unitario']
        mensaje += f"- {prod['nombre']} ({tipo}) x {prod['cantidad']} = ${int(precio * prod['cantidad']):,}\n"
    try:
        fecha_str = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d-%b-%Y %H:%M")
    except Exception:
        fecha_str = fecha
    mensaje += f"\n💰 *Total:* ${int(total):,}\n📅 *Fecha:* {fecha_str}\n🔖 *Estado:* {estado}"
    return mensaje

def enviar_mensaje_whatsapp_greenapi(mensaje):
    id_instance = os.getenv("GREENAPI_ID_INSTANCE")
    api_token = os.getenv("GREENAPI_API_TOKEN")
    numero_destino = os.getenv("GREENAPI_DESTINO")
    if not (id_instance and api_token and numero_destino):
        print("Faltan variables de entorno para Green-API")
        return False
    url = f"https://api.green-api.com/waInstance{id_instance}/sendMessage/{api_token}"
    payload = {
        "chatId": f"{numero_destino}@c.us",
        "message": mensaje
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error enviando mensaje WhatsApp: {e}")
        return False

@router.get("/")
def listar_pedidos(estado: Optional[str] = None):
    try:
        query = supabase.table("pedidos").select("*").order("fecha", desc=True).limit(10)
        if estado:
            if estado not in ["pendiente", "en proceso"]:
                raise HTTPException(status_code=400, detail="Estado debe ser 'pendiente' o 'en proceso'")
            query = query.eq("estado", estado)
        result = query.execute()
        pedidos = result.data
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
    pedido_data = {
        "cliente_id": pedido.cliente_id,
    }
    pedido_result = supabase.table("pedidos").insert(pedido_data).execute()
    if not pedido_result.data:
        raise HTTPException(status_code=400, detail="No se pudo crear el pedido")
    pedido_id = pedido_result.data[0]["id"]
    fecha = pedido_result.data[0].get("fecha")
    estado = pedido_result.data[0].get("estado", "pendiente")
    # Obtener datos del cliente
    cliente = supabase.table("clientes").select("nombre, telefono").eq("id", pedido.cliente_id).single().execute().data
    productos_a_insertar = []
    productos_mensaje = []
    total = 0
    for prod in pedido.productos:
        producto_db = supabase.table("productos").select("nombre, precio, unidades_por_paca").eq("id", prod.producto_id).single().execute().data
        if not producto_db:
            raise HTTPException(status_code=404, detail=f"Producto {prod.producto_id} no encontrado")
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
        productos_mensaje.append({
            "nombre": producto_db["nombre"],
            "tipo": prod.tipo,
            "cantidad": prod.cantidad,
            "precio_unitario": precio_unitario,
            "unidades_por_paca": producto_db["unidades_por_paca"]
        })
        total += precio_unitario * prod.cantidad
    if productos_a_insertar:
        supabase.table("pedido_productos").insert(productos_a_insertar).execute()
    mensaje_whatsapp = armar_mensaje_whatsapp(
        cliente_nombre=cliente["nombre"] if cliente else "N/A",
        cliente_telefono=cliente["telefono"] if cliente else "N/A",
        productos=productos_mensaje,
        total=total,
        fecha=fecha or datetime.now().isoformat(),
        estado=estado
    )
    enviado = enviar_mensaje_whatsapp_greenapi(mensaje_whatsapp)
    return {
        "mensaje": "Pedido creado correctamente",
        "pedido_id": pedido_id,
        "mensaje_whatsapp": mensaje_whatsapp,
        "whatsapp_enviado": enviado
    }