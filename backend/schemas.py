from pydantic import BaseModel
from typing import List

class Producto(BaseModel):
    """
    Modelo de producto. El campo 'precio' está expresado en pesos colombianos (COP).
    """
    id: int | None = None
    nombre: str
    precio: float  # Valor en pesos colombianos (COP)
    unidades_por_paca: int | None = None  # Opcional, null si no aplica

class PedidoProductoCreate(BaseModel):
    producto_id: int
    tipo: str  # 'unidad' o 'paca'
    cantidad: int

class PedidoCreate(BaseModel):
    cliente_id: int
    productos: List[PedidoProductoCreate]