<template>
  <div class="clientes-container">
    <div class="card card-formulario">
      <h2>Crear cliente</h2>
      <form @submit.prevent="crearCliente">
        <div class="form-group">
          <label>Nombre*</label>
          <input v-model.trim="nombre" :class="{ error: nombreError }" />
          <span v-if="nombreError" class="error-msg">{{ nombreError }}</span>
        </div>
        <div class="form-group">
          <label>Teléfono*</label>
          <input v-model.trim="telefono" :class="{ error: telefonoError }" />
          <span v-if="telefonoError" class="error-msg">{{ telefonoError }}</span>
        </div>
        <div class="form-group">
          <label>Dirección</label>
          <input v-model.trim="direccion" />
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="cargando" class="btn btn-primary">{{ editando ? 'Actualizar' : 'Crear' }}</button>
          <button v-if="editando" type="button" @click="cancelarEdicion" class="btn btn-secondary">Cancelar</button>
        </div>
      </form>
      <p v-if="respuesta" class="success-msg">{{ respuesta }}</p>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <p v-if="cargando" class="loading-msg">Procesando...</p>
    </div>
    <div class="card card-listado">
      <h2>Lista de clientes</h2>
      <input v-model="busqueda" @input="buscarClientes" placeholder="Buscar clientes..." class="search-input" />
      <div class="clientes-grid grid-responsive">
        <div v-for="cliente in clientes" :key="cliente.id" class="tarjeta-cliente">
          <div class="cliente-info">
            <span class="cliente-nombre">{{ cliente.nombre }}</span>
            <span class="cliente-tel">
              <span class="info-label">Teléfono:</span>
              {{ cliente.telefono }}
            </span>
            <span class="cliente-dir">
              <span class="info-label">Dirección:</span>
              {{ cliente.direccion }}
            </span>
          </div>
          <div class="cliente-actions">
            <button @click="editarCliente(cliente)" class="btn btn-edit" title="Editar">
              <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 13.5V16h2.5l7.06-7.06-2.5-2.5L4 13.5zM17.71 6.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.13 1.13 3.75 3.75 1.13-1.13z" fill="currentColor"/></svg>
              Editar
            </button>
            <button @click="eliminarCliente(cliente.id)" class="btn btn-delete" title="Eliminar">
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
        <span v-if="totalClientes > 0" class="total-clientes">Total: {{ totalClientes }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      nombre: '',
      telefono: '',
      direccion: '',
      respuesta: '',
      error: '',
      clientes: [],
      pagina: 1,
      limite: 10,
      busqueda: '',
      editando: false,
      idEditando: null,
      nombreError: '',
      telefonoError: '',
      cargando: false,
      nuevoCliente: {
        nombre: '',
        telefono: '',
        email: ''
      },
      totalClientes: 0,
    }
  },
  mounted() {
    this.cargarClientes()
  },
  methods: {
    validarCampos() {
      this.nombreError = ''
      this.telefonoError = ''
      let valido = true
      if (!this.nombre.trim()) {
        this.nombreError = 'El nombre es obligatorio.'
        valido = false
      }
      // Teléfono colombiano: 10 dígitos, empieza por 3, 6 o 7
      const tel = this.telefono.trim()
      if (!tel) {
        this.telefonoError = 'El teléfono es obligatorio.'
        valido = false
      } else if (!/^[3-7][0-9]{9}$/.test(tel)) {
        this.telefonoError = 'Debe ser un número colombiano válido de 10 dígitos.'
        valido = false
      }
      return valido
    },
    async crearCliente() {
      this.respuesta = ''
      this.error = ''
      if (!this.validarCampos()) return
      this.cargando = true
      const apiUrl = import.meta.env.VITE_API_URL
      try {
        // Evitar duplicados por teléfono
        const existe = this.clientes.some(c => c.telefono === this.telefono.trim() && (!this.editando || c.id !== this.idEditando))
        if (existe) {
          this.telefonoError = 'Ya existe un cliente con ese teléfono.'
          this.cargando = false
          return
        }
        if (this.editando) {
          // Editar cliente
          const res = await fetch(`${apiUrl}/clientes/editar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id: this.idEditando,
              nombre: this.nombre.trim(),
              telefono: this.telefono.trim(),
              direccion: this.direccion.trim()
            })
          })
          if (!res.ok) throw new Error('No se pudo editar el cliente')
          await res.json()
          this.respuesta = 'Cliente actualizado'
          this.cancelarEdicion()
        } else {
          // Crear cliente
          const res = await fetch(`${apiUrl}/clientes/crear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              nombre: this.nombre.trim(),
              telefono: this.telefono.trim(),
              direccion: this.direccion.trim()
            })
          })
          if (!res.ok) throw new Error('No se pudo crear el cliente')
          await res.json()
          this.respuesta = 'Cliente creado'
          this.nombre = ''
          this.telefono = ''
          this.direccion = ''
        }
        this.cargarClientes()
      } catch (e) {
        this.error = e.message
      } finally {
        this.cargando = false
      }
    },
    editarCliente(cliente) {
      this.editando = true
      this.idEditando = cliente.id
      this.nombre = cliente.nombre
      this.telefono = cliente.telefono
      this.direccion = cliente.direccion
      this.respuesta = ''
      this.error = ''
      this.nombreError = ''
      this.telefonoError = ''
    },
    cancelarEdicion() {
      this.editando = false
      this.idEditando = null
      this.nombre = ''
      this.telefono = ''
      this.direccion = ''
      this.nombreError = ''
      this.telefonoError = ''
    },
    async eliminarCliente(id) {
      this.respuesta = ''
      this.error = ''
      const apiUrl = import.meta.env.VITE_API_URL
      if (!confirm('¿Seguro que deseas eliminar este cliente?')) return
      this.cargando = true
      try {
        const res = await fetch(`${apiUrl}/clientes/eliminar/${id}`, {
          method: 'DELETE'
        })
        if (!res.ok) throw new Error('No se pudo eliminar el cliente')
        this.respuesta = 'Cliente eliminado'
        this.cargarClientes()
      } catch (e) {
        this.error = e.message
      } finally {
        this.cargando = false
      }
    },
    async cargarClientes() {
      this.error = ''
      try {
        const apiUrl = import.meta.env.VITE_API_URL
        const params = new URLSearchParams({
          page: this.pagina,
          limit: this.limite,
          search: this.busqueda
        })
        const res = await fetch(`${apiUrl}/clientes/?${params}`)
        if (!res.ok) throw new Error('No se pudo cargar la lista de clientes')
        const data = await res.json()
        this.clientes = data.clientes || []
        this.hayMasPaginas = data.hayMasPaginas !== undefined ? data.hayMasPaginas : false
        this.totalClientes = data.total || 0
      } catch (e) {
        this.error = e.message
      }
    },
    paginaAnterior() {
      if (this.pagina > 1) {
        this.pagina--
        this.cargarClientes()
      }
    },
    paginaSiguiente() {
      if (this.hayMasPaginas) {
        this.pagina++
        this.cargarClientes()
      }
    },
    buscarClientes() {
      this.pagina = 1
      this.cargarClientes()
    }
  }
}
</script> 