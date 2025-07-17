<template>
  <div class="pedidos-root">
    <h2>Crear Pedido</h2>
    <form @submit.prevent="agregarProducto">
      <div class="form-group">
        <label>Cliente (nombre):</label>
        <input v-model="nombreCliente" placeholder="Buscar por nombre" @input="buscarCliente" required />
        <div v-if="clientesEncontrados.length > 0 && nombreCliente" class="resultados-busqueda">
          <div v-for="cliente in clientesEncontrados" :key="cliente.id" 
               @click="seleccionarCliente(cliente)" class="resultado-item">
            {{ cliente.nombre }} - {{ cliente.telefono }}
          </div>
        </div>
        <span v-if="cliente">Cliente seleccionado: {{ cliente.nombre }} ({{ cliente.telefono }})</span>
      </div>
      <div class="form-group">
        <label>Producto:</label>
        <input v-model="busquedaProducto" placeholder="Buscar producto por nombre" @input="filtrarProductos" />
        <div v-if="productosFiltrados.length > 0 && busquedaProducto" class="resultados-busqueda">
          <div v-for="prod in productosFiltrados" :key="prod.id" 
               @click="seleccionarProducto(prod)" class="resultado-item">
            {{ prod.nombre }} ({{ prod.precio }} c/u)
            <span v-if="prod.unidades_por_paca && prod.unidades_por_paca > 0"> - {{ prod.unidades_por_paca }} x paca</span>
          </div>
        </div>
      </div>
      <div class="form-group" v-if="productoActual">
        <label>Tipo:</label>
        <select v-model="tipoSeleccionado">
          <option value="unidad">Unidad</option>
          <option v-if="productoActual.unidades_por_paca && productoActual.unidades_por_paca > 0" value="paca">Paca</option>
        </select>
      </div>
      <div class="form-group" v-if="productoActual">
        <label>Cantidad:</label>
        <input type="number" v-model.number="cantidad" min="1" required />
      </div>
      <button type="submit" :disabled="!cliente || !productoActual || !tipoSeleccionado || cantidad < 1">Agregar producto</button>
    </form>

    <div v-if="pedido.productos.length > 0" class="resumen">
      <h3>Resumen del pedido</h3>
      <ul>
        <li v-for="(prod, idx) in pedido.productos" :key="idx">
          {{ mostrarProducto(prod) }}
          <button @click="eliminarProducto(idx)">Eliminar</button>
        </li>
      </ul>
      <button @click="enviarPedido" :disabled="enviando">Enviar pedido</button>
    </div>
    <div v-if="mensaje" class="mensaje-exito">{{ mensaje }}</div>
    <div v-if="error" class="mensaje-error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'Pedidos',
  data() {
    return {
      nombreCliente: '',
      cliente: null,
      clientesEncontrados: [],
      productos: [],
      productosFiltrados: [],
      busquedaProducto: '',
      productoSeleccionadoId: '',
      productoActual: null,
      tipoSeleccionado: 'unidad',
      cantidad: 1,
      pedido: {
        productos: []
      },
      mensaje: '',
      error: '',
      enviando: false
    }
  },
  mounted() {
    this.cargarProductos();
  },
  methods: {
    async cargarProductos() {
      // Cargar todos los productos
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const res = await fetch(`${apiUrl}/productos/`);
        const data = await res.json();
        this.productos = data.productos || data;
        this.productosFiltrados = [];
      } catch (e) {
        this.error = 'Error cargando productos';
      }
    },
    async buscarCliente() {
      if (!this.nombreCliente || this.nombreCliente.length < 2) {
        this.clientesEncontrados = [];
        return;
      }
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const res = await fetch(`${apiUrl}/clientes?search=${this.nombreCliente}`);
        const data = await res.json();
        this.clientesEncontrados = data.clientes || data;
      } catch (e) {
        this.error = 'Error buscando cliente';
        this.clientesEncontrados = [];
      }
    },
    seleccionarCliente(cliente) {
      this.cliente = cliente;
      this.nombreCliente = cliente.nombre;
      this.clientesEncontrados = [];
      this.error = '';
    },
    filtrarProductos() {
      if (!this.busquedaProducto || this.busquedaProducto.length < 2) {
        this.productosFiltrados = [];
        return;
      }
      const busqueda = this.busquedaProducto.toLowerCase();
      this.productosFiltrados = this.productos.filter(prod => 
        prod.nombre.toLowerCase().includes(busqueda)
      );
    },
    seleccionarProducto(producto) {
      this.productoActual = producto;
      this.productoSeleccionadoId = producto.id;
      this.busquedaProducto = producto.nombre;
      this.productosFiltrados = [];
      this.tipoSeleccionado = 'unidad';
      this.cantidad = 1;
    },
    agregarProducto() {
      if (!this.productoActual || !this.tipoSeleccionado || this.cantidad < 1) return;
      // Validación frontend: solo permitir "paca" si el producto tiene unidades_por_paca > 0
      if (this.tipoSeleccionado === 'paca' && (!this.productoActual.unidades_por_paca || this.productoActual.unidades_por_paca <= 0)) {
        this.error = 'Este producto no se vende por paca';
        return;
      }
      this.pedido.productos.push({
        producto_id: this.productoActual.id,
        tipo: this.tipoSeleccionado,
        cantidad: this.cantidad,
        nombre: this.productoActual.nombre,
        unidades_por_paca: this.productoActual.unidades_por_paca,
        precio: this.productoActual.precio
      });
      this.productoSeleccionadoId = '';
      this.productoActual = null;
      this.tipoSeleccionado = 'unidad';
      this.cantidad = 1;
      this.busquedaProducto = '';
      this.error = '';
    },
    eliminarProducto(idx) {
      this.pedido.productos.splice(idx, 1);
    },
    mostrarProducto(prod) {
      let tipo = prod.tipo === 'paca' ? `Paca (${prod.unidades_por_paca} und)` : 'Unidad';
      let precio = prod.tipo === 'paca' ? (prod.precio * prod.unidades_por_paca) : prod.precio;
      return `${prod.nombre} - ${tipo} x ${prod.cantidad} = $${(precio * prod.cantidad).toLocaleString()}`;
    },
    async enviarPedido() {
      if (!this.cliente || this.pedido.productos.length === 0) {
        this.error = 'Debes seleccionar un cliente y agregar al menos un producto';
        return;
      }
      this.enviando = true;
      this.mensaje = '';
      this.error = '';
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const body = {
          cliente_id: this.cliente.id,
          productos: this.pedido.productos.map(p => ({
            producto_id: p.producto_id,
            tipo: p.tipo,
            cantidad: p.cantidad
          }))
        };
        const res = await fetch(`${apiUrl}/pedidos/crear`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error('No se pudo crear el pedido');
        const data = await res.json();
        this.mensaje = `Pedido creado correctamente (ID: ${data.pedido_id})`;
        this.pedido.productos = [];
        this.cliente = null;
        this.nombreCliente = '';
      } catch (e) {
        this.error = e.message || 'Error enviando pedido';
      } finally {
        this.enviando = false;
      }
    }
  }
}
</script>

<style scoped>
.pedidos-root {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.form-group {
  margin-bottom: 1rem;
  position: relative;
}
input, select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  width: 100%;
  font-size: 1rem;
}
.resultados-busqueda {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 4px 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.resultado-item {
  padding: 0.5rem;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}
.resultado-item:hover {
  background: #f5f5f5;
}
.resultado-item:last-child {
  border-bottom: none;
}
button {
  background: #2d8cf0;
  color: #fff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.resumen {
  margin-top: 2rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}
.mensaje-exito {
  color: green;
  margin-top: 1rem;
}
.mensaje-error {
  color: red;
  margin-top: 1rem;
}
</style>

<!-- Hereda estilos globales automáticamente por el import en main.js -->