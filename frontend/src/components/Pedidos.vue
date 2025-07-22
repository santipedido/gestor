<template>
  <div class="pedidos-root">
    <!-- Sección para crear pedidos -->
    <div class="seccion-crear">
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
        <div class="total-pedido">
          <strong>Total del pedido: ${{ totalPedido.toLocaleString() }}</strong>
        </div>
        <button @click="enviarPedido" :disabled="enviando">Enviar pedido</button>
      </div>
    </div>

    <!-- Sección para listar pedidos -->
    <div class="seccion-lista">
      <h2>Pedidos Existentes</h2>
      <div class="filtros">
        <label>Filtrar por estado:</label>
        <select v-model="filtroEstado" @change="cargarPedidos">
          <option value="">Todos</option>
          <option value="pendiente">Pendiente</option>
          <option value="en proceso">En Proceso</option>
        </select>
        <button @click="cargarPedidos" :disabled="cargando">Actualizar</button>
      </div>

      <div v-if="cargando" class="cargando">Cargando pedidos...</div>
      
      <div v-else-if="pedidos.length === 0" class="sin-pedidos">
        No hay pedidos para mostrar
      </div>
      
      <div v-else class="lista-pedidos">
        <div v-for="pedido in pedidos" :key="pedido.id" class="pedido-item">
          <div class="pedido-header">
            <h4>Pedido #{{ pedido.id }}</h4>
            <span class="estado" :class="pedido.estado">{{ pedido.estado }}</span>
          </div>
          <div class="pedido-info">
            <p><strong>Cliente:</strong> {{ pedido.cliente?.nombre || 'N/A' }} ({{ pedido.cliente?.telefono || 'N/A' }})</p>
            <p><strong>Fecha:</strong> {{ formatearFecha(pedido.fecha) }}</p>
          </div>
          <div class="pedido-acciones">
            <button class="btn-ver" @click="toggleDetallesPedido(pedido.id)">
              {{ detallesPedidoId === pedido.id ? 'Ocultar detalles' : 'Ver detalles' }}
            </button>
            <button class="btn-editar" @click="toggleEditarPedido(pedido.id)">
              {{ editarPedidoId === pedido.id ? 'Cancelar edición' : 'Editar' }}
            </button>
            <button class="btn-eliminar" @click="confirmarEliminarPedido(pedido.id)">Eliminar</button>
          </div>

          <!-- Sección expandible de detalles -->
          <div v-if="detallesPedidoId === pedido.id" class="detalles-expandido">
            <div v-if="detallesCargando" class="cargando">Cargando detalles...</div>
            <div v-else-if="detallesError" class="mensaje-error">{{ detallesError }}</div>
            <div v-else-if="detallesPedido" class="detalles-contenido">
              <h5>Detalles del pedido</h5>
              <p><strong>Estado:</strong> {{ detallesPedido.pedido.estado }}</p>
              <p><strong>Cliente:</strong> {{ detallesPedido.cliente?.nombre || 'N/A' }} ({{ detallesPedido.cliente?.telefono || 'N/A' }})</p>
              <p><strong>Fecha:</strong> {{ formatearFecha(detallesPedido.pedido.fecha) }}</p>
              <h6>Productos:</h6>
              <ul>
                <li v-for="(prod, idx) in detallesPedido.productos" :key="idx">
                  {{ prod.nombre }} ({{ prod.tipo === 'paca' ? `Paca de ${prod.unidades_por_paca} und` : 'Unidad' }}) x {{ prod.cantidad }} = ${{ prod.subtotal.toLocaleString() }}
                </li>
              </ul>
              <div class="total-pedido">
                <strong>Total: ${{ detallesPedido.total.toLocaleString() }}</strong>
              </div>
            </div>
          </div>

          <!-- Sección expandible de edición -->
          <div v-if="editarPedidoId === pedido.id" class="editar-expandido">
            <div v-if="editarCargando" class="cargando">Cargando datos para editar...</div>
            <div v-else-if="editarError" class="mensaje-error">{{ editarError }}</div>
            <div v-else-if="editarPedido" class="editar-formulario">
              <h5>Editar pedido</h5>
              <form @submit.prevent="guardarEdicionPedido">
                <div class="form-group">
                  <label>Estado:</label>
                  <select v-model="editarPedido.estado">
                    <option value="pendiente">Pendiente</option>
                    <option value="en proceso">En Proceso</option>
                  </select>
                </div>
                <h6>Productos:</h6>
                <div class="editar-productos">
                  <label>Buscar producto en el pedido:</label>
                  <input v-model="busquedaEditarProducto" placeholder="Buscar producto por nombre en el pedido" />
                  <div v-if="productosFiltradosEdicion.length === 0">
                    <span class="mensaje-error">El producto no está en la lista de este pedido.</span>
                  </div>
                  <div v-for="(prod, idx) in productosPaginadosEdicion" :key="idx" class="form-group">
                    <label>Producto:</label>
                    <input :value="prod.nombre" readonly />
                    <label>Tipo:</label>
                    <select v-model="prod.tipo">
                      <option value="unidad">Unidad</option>
                      <option v-if="getProductoPorId(prod.producto_id)?.unidades_por_paca > 0" value="paca">Paca</option>
                    </select>
                    <label>Cantidad:</label>
                    <input type="number" v-model.number="prod.cantidad" min="1" />
                    <button type="button" @click="eliminarEditarProductoPorId(prod.producto_id)">Eliminar</button>
                  </div>
                  <div class="paginacion">
                    <button @click="cambiarPaginaEdicion(paginaEdicion - 1)" :disabled="paginaEdicion <= 1">Anterior</button>
                    <span>Página {{ paginaEdicion }} de {{ totalPaginasEdicion }}</span>
                    <button @click="cambiarPaginaEdicion(paginaEdicion + 1)" :disabled="paginaEdicion >= totalPaginasEdicion">Siguiente</button>
                  </div>
                  <hr />
                  <label>Agregar producto al pedido:</label>
                  <input v-model="busquedaAgregarProducto" placeholder="Buscar producto para agregar" @input="filtrarAgregarProductos" />
                  <div v-if="mensajeAgregarProducto" class="mensaje-error">{{ mensajeAgregarProducto }}</div>
                  <div v-if="productosFiltradosAgregar.length > 0">
                    <div v-for="p in productosFiltradosAgregar" :key="p.id" class="resultado-item" @click="agregarProductoAEdicion(p)">
                      {{ p.nombre }}
                    </div>
                  </div>
                </div>
                <button type="submit" :disabled="guardandoEdicion">Guardar cambios</button>
              </form>
            </div>
          </div>

        </div>
        <!-- Paginación -->
        <div class="paginacion">
          <button @click="cambiarPagina(paginaActual - 1)" :disabled="paginaActual <= 1">Anterior</button>
          <span>Página {{ paginaActual }} de {{ totalPaginas }}</span>
          <button @click="cambiarPagina(paginaActual + 1)" :disabled="paginaActual >= totalPaginas">Siguiente</button>
        </div>
      </div>
      <!-- Modal de confirmación de eliminación -->
      <div v-if="eliminarPedidoId !== null" class="modal-eliminar">
        <div class="modal-contenido">
          <p>¿Estás seguro de que deseas eliminar este pedido?</p>
          <button @click="eliminarPedido">Sí, eliminar</button>
          <button @click="eliminarPedidoId = null">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- Sección para historial de pedidos por teléfono -->
    <div class="seccion-historial">
      <h2>Historial de pedidos por teléfono</h2>
      <form @submit.prevent="buscarHistorial">
        <div class="form-group">
          <label>Teléfono del cliente:</label>
          <input v-model="telefonoHistorial" placeholder="Ej: 3001234567" required />
          <button type="submit" :disabled="cargandoHistorial">Buscar</button>
        </div>
      </form>
      <div v-if="cargandoHistorial" class="cargando">Buscando historial...</div>
      <div v-else-if="historialError" class="mensaje-error">{{ historialError }}</div>
      <div v-else-if="historialPedidos && historialPedidos.pedidos && historialPedidos.pedidos.length === 0" class="sin-pedidos">
        No hay pedidos para este cliente.
      </div>
      <div v-else-if="historialPedidos && historialPedidos.pedidos && historialPedidos.pedidos.length > 0" class="historial-lista">
        <div class="cliente-info">
          <strong>Cliente:</strong> {{ historialPedidos.cliente.nombre }} ({{ historialPedidos.cliente.telefono }})
        </div>
        <div v-for="(item, idx) in historialPedidos.pedidos" :key="item.pedido.id" class="pedido-item historial">
          <div class="pedido-header">
            <h4>Pedido #{{ item.pedido.id }}</h4>
            <span class="estado" :class="item.pedido.estado">{{ item.pedido.estado }}</span>
          </div>
          <div class="pedido-info">
            <p><strong>Fecha:</strong> {{ formatearFecha(item.pedido.fecha) }}</p>
          </div>
          <h6>Productos:</h6>
          <ul>
            <li v-for="(prod, i) in item.productos" :key="i">
              {{ prod.nombre }} ({{ prod.tipo === 'paca' ? `Paca de ${prod.unidades_por_paca} und` : 'Unidad' }}) x {{ prod.cantidad }} = ${{ prod.subtotal.toLocaleString() }}
            </li>
          </ul>
          <div class="total-pedido">
            <strong>Total: ${{ item.total.toLocaleString() }}</strong>
          </div>
        </div>
      </div>
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
      enviando: false,
      // Nuevos datos para listar pedidos
      pedidos: [],
      filtroEstado: '',
      cargando: false,
      detallesPedidoId: null,
      detallesPedido: null,
      detallesCargando: false,
      detallesError: '',
      telefonoHistorial: '',
      historialPedidos: null,
      cargandoHistorial: false,
      historialError: '',
      editarPedidoId: null,
      editarPedido: null,
      editarCargando: false,
      editarError: '',
      guardandoEdicion: false,
      eliminarPedidoId: null,
      eliminando: false,
      paginaActual: 1,
      totalPaginas: 1,
      busquedaEditarProducto: '',
      paginaEdicion: 1,
      productosPorPaginaEdicion: 5,
      busquedaAgregarProducto: '',
      productosFiltradosAgregar: [],
      mensajeAgregarProducto: ''
    }
  },
  computed: {
    totalPedido() {
      return this.pedido.productos.reduce((total, prod) => {
        let precioUnitario = prod.tipo === 'paca' 
          ? (prod.precio * prod.unidades_por_paca) 
          : prod.precio;
        return total + (precioUnitario * prod.cantidad);
      }, 0);
    },
    totalEditarPedido() {
      if (!this.editarPedido || !this.editarPedido.productos) return 0;
      return this.editarPedido.productos.reduce((total, prod) => {
        const producto = this.getProductoPorId(prod.producto_id);
        let precioUnitario = prod.tipo === 'paca' && producto && producto.unidades_por_paca > 0
          ? (producto.precio * producto.unidades_por_paca)
          : (producto ? producto.precio : 0);
        return total + (precioUnitario * prod.cantidad);
      }, 0);
    },
    productosFiltradosEdicion() {
      if (!this.editarPedido || !this.editarPedido.productos) return [];
      if (!this.busquedaEditarProducto) return this.editarPedido.productos;
      return this.editarPedido.productos.filter(prod => {
        const producto = this.getProductoPorId(prod.producto_id);
        return producto && producto.nombre.toLowerCase().includes(this.busquedaEditarProducto.toLowerCase());
      });
    },
    productosPaginadosEdicion() {
      const start = (this.paginaEdicion - 1) * this.productosPorPaginaEdicion;
      return this.productosFiltradosEdicion.slice(start, start + this.productosPorPaginaEdicion);
    },
    totalPaginasEdicion() {
      return Math.max(1, Math.ceil(this.productosFiltradosEdicion.length / this.productosPorPaginaEdicion));
    }
  },
  mounted() {
    this.cargarProductos();
    this.cargarPedidos();
  },
  methods: {
    async cargarProductos() {
      // Cargar todos los productos
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL('/productos/', apiUrl);
        const res = await fetch(url);
        const data = await res.json();
        this.productos = data.productos || data;
        this.productosFiltrados = [];
      } catch (e) {
        this.error = 'Error cargando productos';
      }
    },
    async cargarPedidos() {
      this.cargando = true;
      this.error = '';
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL('/pedidos/', apiUrl);
        if (this.filtroEstado) {
          url.searchParams.set('estado', this.filtroEstado);
        }
        url.searchParams.set('page', this.paginaActual);
        url.searchParams.set('limit', 10);
        const res = await fetch(url);
        const data = await res.json();
        this.pedidos = data.pedidos || [];
        this.totalPaginas = data.total_paginas || 1;
      } catch (e) {
        this.error = 'Error cargando pedidos';
        this.pedidos = [];
      } finally {
        this.cargando = false;
      }
    },
    formatearFecha(fecha) {
      if (!fecha) return 'N/A';
      return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    async buscarCliente() {
      if (!this.nombreCliente || this.nombreCliente.length < 2) {
        this.clientesEncontrados = [];
        return;
      }
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL('/clientes/', apiUrl);
        url.searchParams.set('search', this.nombreCliente);
        const res = await fetch(url);
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
        const url = new URL('/pedidos/crear', apiUrl);
        const body = {
          cliente_id: this.cliente.id,
          productos: this.pedido.productos.map(p => ({
            producto_id: p.producto_id,
            tipo: p.tipo,
            cantidad: p.cantidad
          }))
        };
        const res = await fetch(url, {
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
        // Recargar la lista de pedidos después de crear uno nuevo
        this.cargarPedidos();
      } catch (e) {
        this.error = e.message || 'Error enviando pedido';
      } finally {
        this.enviando = false;
      }
    },
    async toggleDetallesPedido(id) {
      if (this.detallesPedidoId === id) {
        // Si ya está abierto, lo cerramos
        this.detallesPedidoId = null;
        this.detallesPedido = null;
        this.detallesError = '';
        return;
      }
      this.detallesPedidoId = id;
      this.detallesPedido = null;
      this.detallesCargando = true;
      this.detallesError = '';
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL(`/pedidos/${id}`, apiUrl);
        const res = await fetch(url);
        if (!res.ok) throw new Error('No se pudo obtener el detalle del pedido');
        const data = await res.json();
        this.detallesPedido = data;
      } catch (e) {
        this.detallesError = e.message || 'Error cargando detalles';
      } finally {
        this.detallesCargando = false;
      }
    },
    async buscarHistorial() {
      this.cargandoHistorial = true;
      this.historialError = '';
      this.historialPedidos = null;
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL(`/pedidos/por-telefono/${this.telefonoHistorial}`, apiUrl);
        const res = await fetch(url);
        if (!res.ok) throw new Error('No se encontró el cliente o no hay pedidos');
        const data = await res.json();
        this.historialPedidos = data;
      } catch (e) {
        this.historialError = e.message || 'Error buscando historial';
      } finally {
        this.cargandoHistorial = false;
      }
    },
    async toggleEditarPedido(id) {
      if (this.editarPedidoId === id) {
        this.editarPedidoId = null;
        this.editarPedido = null;
        this.editarError = '';
        this.busquedaEditarProducto = '';
        this.paginaEdicion = 1;
        this.busquedaAgregarProducto = '';
        this.productosFiltradosAgregar = [];
        this.mensajeAgregarProducto = '';
        return;
      }
      this.editarPedidoId = id;
      this.editarPedido = null;
      this.editarCargando = true;
      this.editarError = '';
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL(`/pedidos/${id}`, apiUrl);
        const res = await fetch(url);
        if (!res.ok) throw new Error('No se pudo obtener el pedido para editar');
        const data = await res.json();
        this.editarPedido = {
          id: data.pedido.id,
          estado: data.pedido.estado,
          productos: data.productos.map(p => {
            const prodCatalogo = this.productos.find(prod => prod.nombre === p.nombre);
            return {
              producto_id: prodCatalogo ? prodCatalogo.id : null,
              nombre: p.nombre,
              tipo: p.tipo,
              cantidad: p.cantidad
            };
          })
        };
        this.busquedaEditarProducto = '';
        this.paginaEdicion = 1;
        this.busquedaAgregarProducto = '';
        this.productosFiltradosAgregar = [];
        this.mensajeAgregarProducto = '';
      } catch (e) {
        this.editarError = e.message || 'Error cargando datos para editar';
      } finally {
        this.editarCargando = false;
      }
    },
    getProductoPorId(id) {
      return this.productos.find(p => p.id === id);
    },
    getProductoIdPorNombre(nombre) {
      const prod = this.productos.find(p => p.nombre === nombre);
      return prod ? prod.id : null;
    },
    onEditarProductoChange(idx) {
      // Reset tipo a unidad si el producto no tiene paca
      const prod = this.editarPedido.productos[idx];
      const producto = this.getProductoPorId(prod.producto_id);
      if (producto && (!producto.unidades_por_paca || producto.unidades_por_paca <= 0)) {
        prod.tipo = 'unidad';
      }
    },
    agregarEditarProducto() {
      // No permitir agregar productos en edición
      return;
    },
    eliminarEditarProducto(idx) {
      // No permitir eliminar productos en edición
      return;
    },
    filtrarEditarProductos(idx) {
      // Solo permitir buscar el producto original
      const originalNombre = this.editarPedido.productos[idx].busqueda;
      this.$set(
        this.editarPedido.productos[idx],
        'productosFiltrados',
        this.productos.filter(p => p.nombre === originalNombre)
      );
    },
    seleccionarEditarProducto(idx, producto) {
      // No permitir cambiar el producto
      return;
    },
    async guardarEdicionPedido() {
      this.guardandoEdicion = true;
      this.editarError = '';
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL('/pedidos/actualizar', apiUrl);
        const body = {
          id: this.editarPedido.id,
          estado: this.editarPedido.estado,
          productos: this.editarPedido.productos.map(p => ({
            producto_id: p.producto_id,
            tipo: p.tipo,
            cantidad: p.cantidad
          }))
        };
        const res = await fetch(url, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error('No se pudo actualizar el pedido');
        this.editarPedidoId = null;
        this.editarPedido = null;
        this.cargarPedidos();
      } catch (e) {
        this.editarError = e.message || 'Error guardando cambios';
      } finally {
        this.guardandoEdicion = false;
      }
    },
    confirmarEliminarPedido(id) {
      this.eliminarPedidoId = id;
    },
    async eliminarPedido() {
      if (!this.eliminarPedidoId) return;
      this.eliminando = true;
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const url = new URL(`/pedidos/eliminar/${this.eliminarPedidoId}`, apiUrl);
        const res = await fetch(url, { method: 'DELETE' });
        if (!res.ok) throw new Error('No se pudo eliminar el pedido');
        this.eliminarPedidoId = null;
        this.cargarPedidos();
      } catch (e) {
        alert(e.message || 'Error eliminando pedido');
      } finally {
        this.eliminando = false;
      }
    },
    cambiarPagina(nuevaPagina) {
      if (nuevaPagina < 1 || nuevaPagina > this.totalPaginas) return;
      this.paginaActual = nuevaPagina;
      this.cargarPedidos();
    },
    cambiarPaginaEdicion(nuevaPagina) {
      if (nuevaPagina < 1 || nuevaPagina > this.totalPaginasEdicion) return;
      this.paginaEdicion = nuevaPagina;
    },
    eliminarEditarProductoPorId(producto_id) {
      this.editarPedido.productos = this.editarPedido.productos.filter(p => p.producto_id !== producto_id);
      // Ajustar paginación si es necesario
      if (this.paginaEdicion > this.totalPaginasEdicion) {
        this.paginaEdicion = this.totalPaginasEdicion;
      }
    },
    filtrarAgregarProductos() {
      this.mensajeAgregarProducto = '';
      if (!this.busquedaAgregarProducto || this.busquedaAgregarProducto.length < 2) {
        this.productosFiltradosAgregar = [];
        return;
      }
      const yaEnPedido = this.editarPedido.productos.map(p => p.producto_id);
      this.productosFiltradosAgregar = this.productos.filter(p =>
        p.nombre.toLowerCase().includes(this.busquedaAgregarProducto.toLowerCase()) &&
        !yaEnPedido.includes(p.id)
      );
      if (this.productosFiltradosAgregar.length === 0) {
        // Si el producto ya está en el pedido
        if (this.productos.some(p => p.nombre.toLowerCase().includes(this.busquedaAgregarProducto.toLowerCase()))) {
          this.mensajeAgregarProducto = 'El producto ya está en la lista del pedido.';
        } else {
          this.mensajeAgregarProducto = 'El producto no existe.';
        }
      }
    },
    agregarProductoAEdicion(producto) {
      // Validar que no esté ya en la lista
      if (this.editarPedido.productos.some(p => p.producto_id === producto.id)) {
        this.mensajeAgregarProducto = 'El producto ya está en la lista del pedido.';
        return;
      }
      this.editarPedido.productos.push({
        producto_id: producto.id,
        tipo: producto.unidades_por_paca > 0 ? 'unidad' : 'unidad',
        cantidad: 1
      });
      this.busquedaAgregarProducto = '';
      this.productosFiltradosAgregar = [];
      this.mensajeAgregarProducto = '';
      // Ajustar paginación si es necesario
      if (this.paginaEdicion < this.totalPaginasEdicion) {
        this.paginaEdicion = this.totalPaginasEdicion;
      }
    }
  }
}
</script>

<style scoped>
.pedidos-root {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}

.seccion-crear, .seccion-lista {
  margin-bottom: 3rem;
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
  margin-right: 0.5rem;
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

.total-pedido {
  margin: 1rem 0;
  padding: 1rem;
  background: #e8f4fd;
  border-radius: 4px;
  text-align: center;
  font-size: 1.1rem;
}

/* Estilos para la lista de pedidos */
.filtros {
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filtros select {
  width: auto;
  margin: 0;
}

.cargando, .sin-pedidos {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.lista-pedidos {
  display: grid;
  gap: 1rem;
}

.pedido-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: #fafafa;
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.pedido-header h4 {
  margin: 0;
  color: #333;
}

.estado {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.estado.pendiente {
  background: #fff3cd;
  color: #856404;
}

.estado.en\ proceso {
  background: #d1ecf1;
  color: #0c5460;
}

.pedido-info {
  margin-bottom: 1rem;
}

.pedido-info p {
  margin: 0.25rem 0;
  color: #666;
}

.pedido-acciones {
  display: flex;
  gap: 0.5rem;
}

.btn-ver {
  background: #17a2b8;
}

.btn-editar {
  background: #ffc107;
  color: #212529;
}

.btn-eliminar {
  background: #dc3545;
}

.mensaje-exito {
  color: green;
  margin-top: 1rem;
}

.mensaje-error {
  color: red;
  margin-top: 1rem;
}

.detalles-expandido {
  background: #f4f8fb;
  border-radius: 8px;
  margin-top: 1rem;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.detalles-contenido h5 {
  margin-top: 0;
}
.detalles-contenido ul {
  margin: 0 0 1rem 0;
  padding-left: 1.2rem;
}
.seccion-historial {
  margin-top: 3rem;
  padding: 2rem;
  background: #f7fafd;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.historial-lista {
  margin-top: 1rem;
}
.cliente-info {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}
.pedido-item.historial {
  margin-bottom: 2rem;
}
.editar-expandido {
  background: #fffbe6;
  border-radius: 8px;
  margin-top: 1rem;
  padding: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.editar-formulario h5 {
  margin-top: 0;
}
.editar-productos {
  margin-top: 1rem;
}
.editar-productos label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.editar-productos input[type="text"] {
  width: calc(100% - 1rem); /* Adjust for button */
  margin-bottom: 0.5rem;
}
.editar-productos select {
  width: calc(100% - 1rem); /* Adjust for button */
  margin-bottom: 0.5rem;
}
.editar-productos input[type="number"] {
  width: calc(100% - 1rem); /* Adjust for button */
  margin-bottom: 0.5rem;
}
.editar-productos button {
  width: calc(100% - 1rem); /* Adjust for button */
  margin-top: 0.5rem;
}
.editar-productos .paginacion {
  margin-top: 1rem;
}
.editar-productos .paginacion button {
  background: #2d8cf0;
  color: #fff;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
}
.editar-productos .paginacion button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.modal-eliminar {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-contenido {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  text-align: center;
}
.modal-contenido button {
  margin: 0 1rem;
}
.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 2rem 0 0 0;
}
.paginacion button {
  background: #2d8cf0;
  color: #fff;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
}
.paginacion button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>

<!-- Hereda estilos globales automáticamente por el import en main.js -->