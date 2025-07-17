<template>
  <div class="productos-container">
    <div class="card card-formulario">
      <h2>Crear producto</h2>
      <form @submit.prevent="crearProducto">
        <div class="form-group">
          <label>Nombre*</label>
          <input v-model.trim="nombre" :class="{ error: nombreError }" />
          <span v-if="nombreError" class="error-msg">{{ nombreError }}</span>
        </div>
        <div class="form-group">
          <label>Precio (COP)*</label>
          <input v-model.number="precio" type="number" step="0.01" min="0" :class="{ error: precioError }" />
          <span v-if="precioError" class="error-msg">{{ precioError }}</span>
        </div>
        <div class="form-group">
          <label>Unidades por paca (opcional)</label>
          <input v-model.number="unidadesPorPaca" type="number" min="1" placeholder="Dejar vacío si no aplica" />
          <small class="form-help">Cantidad de unidades que trae una paca. Dejar vacío si el producto no se vende por paca.</small>
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="cargando" class="btn btn-primary">{{ editando ? 'Actualizar' : 'Crear' }}</button>
          <button v-if="editando" type="button" @click="cancelarEdicion" class="btn btn-secondary">Cancelar</button>
        </div>
      </form>
      <p v-if="respuesta" class="success-msg show-msg">{{ respuesta }}</p>
      <p v-if="error" class="error-msg show-msg">{{ error }}</p>
      <p v-if="cargando" class="loading-msg">Procesando...</p>
    </div>
    <div v-if="productosImportados.length" class="preview-importacion">
      <h3>Vista previa de importación</h3>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Precio (COP)</th>
            <th>Unidades por paca</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(prod, idx) in productosImportados" :key="idx">
            <td>{{ prod.nombre }}</td>
            <td>${{ Number(prod.precio).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
            <td>{{ prod.unidades_por_paca || 'No aplica' }}</td>
          </tr>
        </tbody>
      </table>
      <button class="btn btn-primary" @click="importarProductos">Importar productos</button>
      <button class="btn btn-secondary" @click="cancelarImportacion">Cancelar</button>
    </div>
    <div class="card card-listado">
      <div class="listado-header">
        <h2>Lista de productos</h2>
        <div class="importar-archivo">
          <label for="archivoExcel" class="btn btn-primary">Importar desde Excel/CSV</label>
          <input id="archivoExcel" type="file" accept=".xlsx,.csv" @change="leerArchivoExcel" style="display:none" />
        </div>
      </div>
      <input v-model="busqueda" @input="buscarProductos" placeholder="Buscar productos..." class="search-input" />
      <div class="productos-grid grid-responsive">
        <div v-for="producto in productos" :key="producto.id" class="tarjeta-producto">
          <div class="producto-info">
            <span class="producto-nombre">{{ producto.nombre }}</span>
            <span class="producto-precio">
              <span class="info-label">Precio:</span>
              ${{ Number(producto.precio).toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
            <span v-if="producto.unidades_por_paca" class="producto-paca">
              <span class="info-label">Paca:</span> {{ producto.unidades_por_paca }} unidades - 
              ${{ (Number(producto.precio) * producto.unidades_por_paca).toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
          </div>
          <div class="producto-actions">
            <button @click="editarProducto(producto)" class="btn btn-edit" title="Editar">
              <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 13.5V16h2.5l7.06-7.06-2.5-2.5L4 13.5zM17.71 6.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.13 1.13 3.75 3.75 1.13-1.13z" fill="currentColor"/></svg>
              Editar
            </button>
            <button @click="eliminarProducto(producto.id)" class="btn btn-delete" title="Eliminar">
              <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 7v7a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V7M9 10v3m2-3v3M4 7h12M8 4h4a1 1 0 0 1 1 1v1H7V5a1 1 0 0 1 1-1z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              Eliminar
            </button>
          </div>
        </div>
      </div>
      <div class="paginacion">
        <button @click="paginaAnterior" :disabled="pagina === 1" class="btn btn-secondary">Anterior</button>
        <span>Página {{ pagina }}</span>
        <button @click="paginaSiguiente" :disabled="!hayMasPaginas" class="btn btn-secondary">Siguiente</button>
        <span v-if="totalProductos > 0" class="total-productos">Total: {{ totalProductos }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx';

export default {
  data() {
    return {
      nombre: '',
      precio: '',
      unidadesPorPaca: '',
      respuesta: '',
      error: '',
      productos: [],
      pagina: 1,
      limite: 10,
      busqueda: '',
      editando: false,
      idEditando: null,
      nombreError: '',
      precioError: '',
      cargando: false,
      productosImportados: [],
      totalProductos: 0
    }
  },
  mounted() {
    this.cargarProductos()
  },
  methods: {
    validarCampos() {
      this.nombreError = ''
      this.precioError = ''
      let valido = true
      if (!this.nombre.trim()) {
        this.nombreError = 'El nombre es obligatorio.'
        valido = false
      } else if (this.productos.some(p => p.nombre.trim().toLowerCase() === this.nombre.trim().toLowerCase() && (!this.editando || p.id !== this.idEditando))) {
        this.nombreError = 'Ya existe un producto con ese nombre.'
        valido = false
      }
      if (this.precio === '' || isNaN(this.precio) || Number(this.precio) <= 0) {
        this.precioError = 'El precio debe ser un número mayor a cero.'
        valido = false
      }
      if (this.unidadesPorPaca !== '' && (isNaN(this.unidadesPorPaca) || Number(this.unidadesPorPaca) < 1)) {
        this.precioError = 'Las unidades por paca deben ser un número mayor a cero.'
        valido = false
      }
      return valido
    },
    async crearProducto() {
      this.respuesta = ''
      this.error = ''
      if (!this.validarCampos()) return
      this.cargando = true
      const apiUrl = import.meta.env.VITE_API_URL
      try {
        if (this.editando) {
          // Editar producto
          const res = await fetch(`${apiUrl}/productos/editar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id: this.idEditando,
              nombre: this.nombre.trim(),
              precio: Number(this.precio),
              unidades_por_paca: this.unidadesPorPaca === '' ? null : Number(this.unidadesPorPaca)
            })
          })
          if (!res.ok) throw new Error((await res.json()).detail || 'No se pudo editar el producto')
          await res.json()
          this.respuesta = '¡Producto actualizado exitosamente!'
          this.cancelarEdicion()
        } else {
          // Crear producto
          const res = await fetch(`${apiUrl}/productos/crear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              nombre: this.nombre.trim(),
              precio: Number(this.precio),
              unidades_por_paca: this.unidadesPorPaca === '' ? null : Number(this.unidadesPorPaca)
            })
          })
          if (!res.ok) throw new Error((await res.json()).detail || 'No se pudo crear el producto')
          await res.json()
          this.respuesta = '¡Producto creado exitosamente!'
          this.nombre = ''
          this.precio = ''
          this.unidadesPorPaca = ''
        }
        this.cargarProductos()
        this.ocultarMensajes()
      } catch (e) {
        this.error = e.message
        this.ocultarMensajes()
      } finally {
        this.cargando = false
      }
    },
    editarProducto(producto) {
      this.editando = true
      this.idEditando = producto.id
      this.nombre = producto.nombre
      this.precio = producto.precio
      this.unidadesPorPaca = producto.unidades_por_paca || ''
      this.respuesta = ''
      this.error = ''
      this.nombreError = ''
      this.precioError = ''
    },
    cancelarEdicion() {
      this.editando = false
      this.idEditando = null
      this.nombre = ''
      this.precio = ''
      this.unidadesPorPaca = ''
      this.nombreError = ''
      this.precioError = ''
    },
    async eliminarProducto(id) {
      this.respuesta = ''
      this.error = ''
      const apiUrl = import.meta.env.VITE_API_URL
      if (!confirm('¿Seguro que deseas eliminar este producto? Esta acción no se puede deshacer.')) return
      this.cargando = true
      try {
        const res = await fetch(`${apiUrl}/productos/eliminar/${id}`, {
          method: 'DELETE'
        })
        if (!res.ok) throw new Error((await res.json()).detail || 'No se pudo eliminar el producto')
        this.respuesta = '¡Producto eliminado exitosamente!'
        this.cargarProductos()
        this.ocultarMensajes()
      } catch (e) {
        this.error = e.message
        this.ocultarMensajes()
      } finally {
        this.cargando = false
      }
    },
    async cargarProductos() {
      this.error = ''
      try {
        const apiUrl = import.meta.env.VITE_API_URL
        const params = new URLSearchParams({
          page: this.pagina,
          limit: this.limite,
          search: this.busqueda
        })
        const res = await fetch(`${apiUrl}/productos/?${params}`)
        if (!res.ok) throw new Error('No se pudo cargar la lista de productos')
        const data = await res.json()
        this.productos = data.productos || []
        this.hayMasPaginas = data.hayMasPaginas !== undefined ? data.hayMasPaginas : false
        this.totalProductos = data.total || 0
      } catch (e) {
        this.error = e.message
      }
    },
    paginaAnterior() {
      if (this.pagina > 1) {
        this.pagina--
        this.cargarProductos()
      }
    },
    paginaSiguiente() {
      if (this.hayMasPaginas) {
        this.pagina++
        this.cargarProductos()
      }
    },
    buscarProductos() {
      this.pagina = 1
      this.cargarProductos()
    },
    ocultarMensajes() {
      setTimeout(() => {
        this.respuesta = ''
        this.error = ''
      }, 3000)
    },
    async leerArchivoExcel(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        let data = new Uint8Array(e.target.result);
        let workbook = XLSX.read(data, { type: 'array' });
        let sheet = workbook.Sheets[workbook.SheetNames[0]];
        let json = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        // Espera encabezados: nombre, precio, unidades_por_paca (opcional)
        let headers = json[0].map(h => h.toString().toLowerCase().trim());
        let idxNombre = headers.indexOf('nombre');
        let idxPrecio = headers.indexOf('precio');
        let idxUnidadesPaca = headers.indexOf('unidades_por_paca');
        if (idxNombre === -1 || idxPrecio === -1) {
          this.error = 'El archivo debe tener columnas "nombre" y "precio".';
          this.ocultarMensajes();
          return;
        }
        let productos = [];
        for (let i = 1; i < json.length; i++) {
          let row = json[i];
          if (!row[idxNombre] || !row[idxPrecio]) continue;
          productos.push({
            nombre: row[idxNombre].toString().trim(),
            precio: parseFloat(row[idxPrecio]),
            unidades_por_paca: idxUnidadesPaca !== -1 && row[idxUnidadesPaca] ? parseInt(row[idxUnidadesPaca]) : null
          });
        }
        if (!productos.length) {
          this.error = 'No se encontraron productos válidos en el archivo.';
          this.ocultarMensajes();
          return;
        }
        this.productosImportados = productos;
      };
      reader.readAsArrayBuffer(file);
    },
    async importarProductos() {
      if (!this.productosImportados.length) return;
      const apiUrl = import.meta.env.VITE_API_URL;
      this.cargando = true;
      try {
        const res = await fetch(`${apiUrl}/productos/importar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ productos: this.productosImportados })
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'No se pudo importar los productos');
        this.respuesta = '¡Productos importados exitosamente!';
        this.productosImportados = [];
        this.cargarProductos();
        this.ocultarMensajes();
      } catch (e) {
        this.error = e.message;
        this.ocultarMensajes();
      } finally {
        this.cargando = false;
      }
    },
    cancelarImportacion() {
      this.productosImportados = [];
    }
  }
}
</script> 