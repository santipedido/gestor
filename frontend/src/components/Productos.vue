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
      <div class="productos-grid">
        <div v-for="producto in productos" :key="producto.id" class="tarjeta-producto">
          <div class="producto-info">
            <span class="producto-nombre">{{ producto.nombre }}</span>
            <span class="producto-precio">
              ${{ Number(producto.precio).toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
            <span v-if="producto.unidades_por_paca" class="producto-paca">
              Paca: {{ producto.unidades_por_paca }} unidades - 
              ${{ (Number(producto.precio) * producto.unidades_por_paca).toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
          </div>
          <div class="producto-actions">
            <button @click="editarProducto(producto)" class="btn btn-edit">Editar</button>
            <button @click="eliminarProducto(producto.id)" class="btn btn-delete">Eliminar</button>
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
        const res = await fetch(`${apiUrl}/productos?${params}`)
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

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

.productos-container {
  display: flex;
  flex-direction: row;
  gap: 2.5rem;
  align-items: flex-start;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1rem;
  box-sizing: border-box;
}
.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  padding: 2rem 2.5rem;
  width: 100%;
  box-sizing: border-box;
}
.card-formulario {
  max-width: 400px;
  min-width: 0;
  flex: 1 1 320px;
}
.card-listado {
  flex: 3 1 0;
  min-width: 0;
}
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  width: 100%;
  margin-top: 2rem;
  box-sizing: border-box;
}
.tarjeta-producto {
  background: #f8fafc;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 1.5rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  box-sizing: border-box;
}
.producto-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.producto-nombre {
  font-weight: 800;
  color: #22223b;
  font-size: 1.08em;
  letter-spacing: 0.01em;
}
.producto-precio {
  color: #2563eb;
  font-size: 0.98em;
  font-weight: 600;
}
.producto-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-left: auto;
}
.paginacion {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  justify-content: center;
  margin-top: 1.5rem;
}

h2 {
  color: #2563eb;
  margin-bottom: 1.5rem;
  font-size: 1.7rem;
  font-weight: 800;
  text-align: center;
  letter-spacing: 0.01em;
}

.form-group {
  margin-bottom: 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group label {
  font-size: 1.08rem;
  color: #64748b;
  font-weight: 600;
}
.form-group input {
  padding: 0.8rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 1rem;
  font-size: 1.08rem;
  outline: none;
  background: #f8fafc;
  color: #22223b;
  transition: border 0.2s, background 0.2s;
  box-shadow: 0 1px 4px rgba(30, 64, 175, 0.04);
}
.form-group input:focus {
  border-color: #2563eb;
  background: #fff;
}
.form-group input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.form-actions {
  display: flex;
  gap: 0.8rem;
  margin-top: 1.2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.55rem 1.3rem;
  border: none;
  border-radius: 0.8rem;
  font-size: 1rem;
  cursor: pointer;
  font-weight: 700;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s, border 0.2s;
  box-shadow: 0 2px 8px rgba(30, 64, 175, 0.08);
  margin-bottom: 0.1rem;
  letter-spacing: 0.01em;
}
.btn-primary {
  background: #2563eb;
  color: #fff;
}
.btn-primary:hover {
  background: #1e40af;
}
.btn-secondary {
  background: #fff;
  color: #2563eb;
  border: 2px solid #2563eb;
}
.btn-secondary:hover {
  background: #2563eb;
  color: #fff;
}
.btn-secondary:disabled {
  background: #e5e7eb;
  color: #b6b6b6;
  cursor: not-allowed;
  border: 2px solid #e5e7eb;
}
.btn-edit {
  background: #22c55e;
  color: #fff;
  margin-right: 0.5rem;
  border: 2px solid #22c55e;
  padding: 0.5rem 1.1rem;
  font-size: 0.98rem;
}
.btn-edit:hover {
  background: #16a34a;
}
.btn-delete {
  background: #ef4444;
  color: #fff;
  border: 2px solid #ef4444;
  padding: 0.5rem 1.1rem;
  font-size: 0.98rem;
}
.btn-delete:hover {
  background: #b91c1c;
}
.success-msg.show-msg, .error-msg.show-msg {
  padding: 0.7rem 1.2rem;
  border-radius: 0.8rem;
  margin-top: 1rem;
  font-size: 1.07rem;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  display: inline-block;
}
.success-msg.show-msg {
  background: #eafaf1;
  color: #27ae60;
  border: 2px solid #27ae60;
}
.error-msg.show-msg {
  background: #fff0f0;
  color: #e74c3c;
  border: 2px solid #e74c3c;
}
.listado-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.importar-archivo {
  margin-bottom: 0;
}
.search-input {
  padding: 0.8rem 1rem;
  border-radius: 1rem;
  border: 2px solid #e5e7eb;
  margin-bottom: 1.2rem;
  font-size: 1.08rem;
  background: #f8fafc;
  color: #22223b;
  transition: border 0.2s, background 0.2s;
  box-shadow: 0 1px 4px rgba(30, 64, 175, 0.04);
  outline: none;
}
.search-input:focus {
  border-color: #2563eb;
  background: #fff;
}
.total-productos {
  color: #64748b;
  font-size: 0.98em;
  margin-left: 1.2rem;
}
.form-help {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 0.2rem;
}
.producto-paca {
  color: #16a34a;
  font-size: 0.95em;
  font-weight: 500;
}
@media (max-width: 900px) {
  .productos-container {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1rem 0.5rem;
  }
  .card-formulario {
    max-width: 100%;
    margin-bottom: 1.5rem;
  }
  .listado-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.7rem;
  }
  .importar-archivo {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
@media (max-width: 600px) {
  .productos-container {
    padding: 0.5rem 0.2rem;
  }
  .card {
    padding: 1rem;
  }
  .productos-grid {
    flex-direction: column;
    gap: 0.8rem;
    display: flex;
  }
  .tarjeta-producto {
    min-width: unset;
    padding: 0.8rem;
  }
  .form-group input, .search-input {
    font-size: 0.98rem;
    padding: 0.4rem;
  }
  .btn {
    font-size: 0.98rem;
    padding: 0.4rem 0.8rem;
  }
  .preview-importacion {
    padding: 0.7rem;
  }
  .preview-importacion th, .preview-importacion td {
    padding: 0.3rem 0.5rem;
    font-size: 0.97rem;
  }
  .paginacion {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
}
</style> 