from fastapi import APIRouter, HTTPException, Body
from database import supabase
from schemas import PedidoCreate
from typing import Optional
from datetime import datetime
import os
import requests
from pydantic import BaseModel

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

def armar_mensaje_edicion_whatsapp(pedido_id, cliente, cambios, fecha):
    mensaje = f"""✏️ *Pedido editado*

#️⃣ *Pedido:* {pedido_id}
👤 *Cliente:* {cliente.get('nombre', 'N/A')}
📞 *Teléfono:* {cliente.get('telefono', 'N/A')}
📅 *Fecha de edición:* {fecha}
"""
    if cambios.get('estado'):
        mensaje += f"\n🔖 *Estado:* de {cambios['estado']['antes']} a {cambios['estado']['despues']}"
    if cambios.get('productos_agregados'):
        mensaje += "\n➕ *Productos agregados:*"
        for p in cambios['productos_agregados']:
            tipo = f"Paca de {p['unidades_por_paca']} und" if p['tipo'] == 'paca' else 'Unidad'
            mensaje += f"\n- {p['nombre']} ({tipo}) x {p['cantidad']}"
    if cambios.get('productos_eliminados'):
        mensaje += "\n➖ *Productos eliminados:*"
        for p in cambios['productos_eliminados']:
            tipo = f"Paca de {p['unidades_por_paca']} und" if p['tipo'] == 'paca' else 'Unidad'
            mensaje += f"\n- {p['nombre']} ({tipo}) x {p['cantidad']}"
    if cambios.get('productos_modificados'):
        mensaje += "\n🔄 *Productos modificados:*"
        for p in cambios['productos_modificados']:
            tipo_antes = f"Paca de {p['antes']['unidades_por_paca']} und" if p['antes']['tipo'] == 'paca' else 'Unidad'
            tipo_despues = f"Paca de {p['despues']['unidades_por_paca']} und" if p['despues']['tipo'] == 'paca' else 'Unidad'
            mensaje += f"\n- {p['antes']['nombre']}: cantidad {p['antes']['cantidad']}→{p['despues']['cantidad']}, tipo {tipo_antes}→{tipo_despues}"
    return mensaje

def comparar_productos_antes_despues(antes, despues):
    # antes y despues: listas de dicts con producto_id, nombre, tipo, cantidad, unidades_por_paca
    antes_dict = {p['producto_id']: p for p in antes}
    despues_dict = {p['producto_id']: p for p in despues}
    agregados = [p for pid, p in despues_dict.items() if pid not in antes_dict]
    eliminados = [p for pid, p in antes_dict.items() if pid not in despues_dict]
    modificados = []
    for pid in antes_dict:
        if pid in despues_dict:
            a, d = antes_dict[pid], despues_dict[pid]
            if a['cantidad'] != d['cantidad'] or a['tipo'] != d['tipo']:
                modificados.append({'antes': a, 'despues': d})
    return agregados, eliminados, modificados

class PedidoProductoUpdate(BaseModel):
    producto_id: int
    tipo: str  # 'unidad' o 'paca'
    cantidad: int

class PedidoUpdate(BaseModel):
    id: int
    estado: Optional[str] = None
    productos: Optional[list[PedidoProductoUpdate]] = None

@router.get("/")
def listar_pedidos(estado: Optional[str] = None, page: int = 1, limit: int = 10):
    try:
        # Construir query base
        query = supabase.table("pedidos").select("*").order("fecha", desc=True)
        if estado:
            if estado not in ["pendiente", "en proceso"]:
                raise HTTPException(status_code=400, detail="Estado debe ser 'pendiente' o 'en proceso'")
            query = query.eq("estado", estado)
        # Paginación
        from_ = (page - 1) * limit
        to_ = from_ + limit - 1
        result = query.range(from_, to_).execute()
        pedidos = result.data
        # Obtener información del cliente para cada pedido
        for pedido in pedidos:
            if pedido.get("cliente_id"):
                cliente = supabase.table("clientes").select("nombre, telefono").eq("id", pedido["cliente_id"]).single().execute()
                if cliente.data:
                    pedido["cliente"] = cliente.data
        # Calcular total de pedidos y páginas
        total_query = supabase.table("pedidos").select("id")
        if estado:
            total_query = total_query.eq("estado", estado)
        total_result = total_query.execute()
        total = len(total_result.data)
        total_paginas = (total + limit - 1) // limit
        return {
            "pedidos": pedidos,
            "total": total,
            "pagina": page,
            "por_pagina": limit,
            "total_paginas": total_paginas
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/por-telefono/{telefono}")
def historial_pedidos_por_telefono(telefono: str):
    try:
        # Buscar cliente por teléfono
        cliente_result = supabase.table("clientes").select("id, nombre, telefono").eq("telefono", telefono).single().execute()
        cliente = cliente_result.data
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        # Buscar pedidos del cliente
        pedidos_result = supabase.table("pedidos").select("*").eq("cliente_id", cliente["id"]).order("fecha", desc=True).limit(10).execute()
        pedidos = pedidos_result.data or []
        pedidos_detalle = []
        for pedido in pedidos:
            productos_result = supabase.table("pedido_productos").select("*").eq("pedido_id", pedido["id"]).execute()
            productos = productos_result.data or []
            productos_detalle = []
            total = 0
            for prod in productos:
                producto_db = supabase.table("productos").select("nombre, unidades_por_paca").eq("id", prod["producto_id"]).single().execute().data
                nombre = producto_db["nombre"] if producto_db else "N/A"
                unidades_por_paca = producto_db["unidades_por_paca"] if producto_db else None
                subtotal = prod["precio_unitario"] * prod["cantidad"]
                total += subtotal
                productos_detalle.append({
                    "nombre": nombre,
                    "tipo": prod["tipo"],
                    "cantidad": prod["cantidad"],
                    "precio_unitario": prod["precio_unitario"],
                    "unidades_por_paca": unidades_por_paca,
                    "subtotal": subtotal
                })
            pedidos_detalle.append({
                "pedido": pedido,
                "productos": productos_detalle,
                "total": total
            })
        return {
            "cliente": cliente,
            "pedidos": pedidos_detalle
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}")
def obtener_pedido(id: int):
    try:
        # Obtener el pedido
        pedido_result = supabase.table("pedidos").select("*").eq("id", id).single().execute()
        pedido = pedido_result.data
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        # Obtener datos del cliente
        cliente = None
        if pedido.get("cliente_id"):
            cliente_result = supabase.table("clientes").select("nombre, telefono").eq("id", pedido["cliente_id"]).single().execute()
            cliente = cliente_result.data if cliente_result.data else None
        # Obtener productos del pedido
        productos_result = supabase.table("pedido_productos").select("*").eq("pedido_id", id).execute()
        productos = productos_result.data or []
        productos_detalle = []
        total = 0
        for prod in productos:
            producto_db = supabase.table("productos").select("nombre, unidades_por_paca").eq("id", prod["producto_id"]).single().execute().data
            nombre = producto_db["nombre"] if producto_db else "N/A"
            unidades_por_paca = producto_db["unidades_por_paca"] if producto_db else None
            subtotal = prod["precio_unitario"] * prod["cantidad"]
            total += subtotal
            productos_detalle.append({
                "nombre": nombre,
                "tipo": prod["tipo"],
                "cantidad": prod["cantidad"],
                "precio_unitario": prod["precio_unitario"],
                "unidades_por_paca": unidades_por_paca,
                "subtotal": subtotal
            })
        return {
            "pedido": pedido,
            "cliente": cliente,
            "productos": productos_detalle,
            "total": total
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

@router.put("/actualizar")
def actualizar_pedido(pedido: PedidoUpdate = Body(...)):
    try:
        # Obtener estado y productos antes de la edición
        pedido_result = supabase.table("pedidos").select("*").eq("id", pedido.id).single().execute()
        if not pedido_result.data:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        pedido_antes = pedido_result.data
        productos_antes_result = supabase.table("pedido_productos").select("*").eq("pedido_id", pedido.id).execute()
        productos_antes = productos_antes_result.data or []
        productos_antes_detalle = []
        for prod in productos_antes:
            producto_db = supabase.table("productos").select("nombre, unidades_por_paca").eq("id", prod["producto_id"]).single().execute().data
            productos_antes_detalle.append({
                "producto_id": prod["producto_id"],
                "nombre": producto_db["nombre"] if producto_db else "N/A",
                "tipo": prod["tipo"],
                "cantidad": prod["cantidad"],
                "unidades_por_paca": producto_db["unidades_por_paca"] if producto_db else None
            })
        # Actualizar estado si se proporciona
        estado_cambio = None
        if pedido.estado:
            if pedido.estado not in ["pendiente", "en proceso"]:
                raise HTTPException(status_code=400, detail="Estado debe ser 'pendiente' o 'en proceso'")
            if pedido_antes["estado"] != pedido.estado:
                estado_cambio = {"antes": pedido_antes["estado"], "despues": pedido.estado}
            supabase.table("pedidos").update({"estado": pedido.estado}).eq("id", pedido.id).execute()
        # Actualizar productos si se proporciona
        productos_despues_detalle = productos_antes_detalle
        if pedido.productos is not None:
            supabase.table("pedido_productos").delete().eq("pedido_id", pedido.id).execute()
            productos_a_insertar = []
            productos_despues_detalle = []
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
                    "pedido_id": pedido.id,
                    "producto_id": prod.producto_id,
                    "tipo": prod.tipo,
                    "cantidad": prod.cantidad,
                    "precio_unitario": precio_unitario
                })
                productos_despues_detalle.append({
                    "producto_id": prod.producto_id,
                    "nombre": producto_db["nombre"],
                    "tipo": prod.tipo,
                    "cantidad": prod.cantidad,
                    "unidades_por_paca": producto_db["unidades_por_paca"]
                })
            if productos_a_insertar:
                supabase.table("pedido_productos").insert(productos_a_insertar).execute()
        # Obtener datos del cliente
        cliente = supabase.table("clientes").select("nombre, telefono").eq("id", pedido_antes["cliente_id"]).single().execute().data
        # Comparar cambios
        agregados, eliminados, modificados = comparar_productos_antes_despues(productos_antes_detalle, productos_despues_detalle)
        cambios = {}
        if estado_cambio:
            cambios['estado'] = estado_cambio
        if agregados:
            cambios['productos_agregados'] = agregados
        if eliminados:
            cambios['productos_eliminados'] = eliminados
        if modificados:
            cambios['productos_modificados'] = modificados
        # Enviar mensaje solo si hubo cambios
        if cambios:
            from datetime import datetime as dt
            fecha_edicion = dt.now().strftime("%d-%b-%Y %H:%M")
            mensaje_edicion = armar_mensaje_edicion_whatsapp(pedido.id, cliente, cambios, fecha_edicion)
            enviar_mensaje_whatsapp_greenapi(mensaje_edicion)
        return {"mensaje": "Pedido actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/eliminar/{id}")
def eliminar_pedido(id: int):
    try:
        # Verificar que el pedido existe
        pedido_result = supabase.table("pedidos").select("id").eq("id", id).single().execute()
        if not pedido_result.data:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        # Eliminar productos asociados
        supabase.table("pedido_productos").delete().eq("pedido_id", id).execute()
        # Eliminar el pedido
        supabase.table("pedidos").delete().eq("id", id).execute()
        return {"mensaje": "Pedido eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))