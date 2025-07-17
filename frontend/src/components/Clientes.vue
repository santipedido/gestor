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
      <div class="clientes-grid">
        <div v-for="cliente in clientes" :key="cliente.id" class="tarjeta-cliente">
          <div class="cliente-info">
            <span class="cliente-nombre">{{ cliente.nombre }}</span>
            <span class="cliente-tel">{{ cliente.telefono }}</span>
            <span class="cliente-dir">{{ cliente.direccion }}</span>
          </div>
          <div class="cliente-actions">
            <button @click="editarCliente(cliente)" class="btn btn-edit">Editar</button>
            <button @click="eliminarCliente(cliente.id)" class="btn btn-delete">Eliminar</button>
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
        // const params = new URLSearchParams({
        //   page: this.pagina,
        //   limit: this.limite,
        //   search: this.busqueda
        // })
        // const res = await fetch(`${apiUrl}/clientes?${params}`)
        const res = await fetch(`${apiUrl}/clientes`)
        if (!res.ok) throw new Error('No se pudo cargar la lista de clientes')
        const data = await res.json()
        this.clientes = data.clientes || []
        // this.hayMasPaginas = data.hayMasPaginas !== undefined ? data.hayMasPaginas : false
        // this.totalClientes = data.total || 0
      } catch (e) {
        this.error = e.message
      }
    },
    // paginaAnterior() {
    //   if (this.pagina > 1) {
    //     this.pagina--
    //     this.cargarClientes()
    //   }
    // },
    // paginaSiguiente() {
    //   if (this.hayMasPaginas) {
    //     this.pagina++
    //     this.cargarClientes()
    //   }
    // },
    // buscarClientes() {
    //   this.pagina = 1
    //   this.cargarClientes()
    // }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

body {
  background: #f7fafd;
  font-family: 'Roboto', 'Inter', 'Segoe UI', Arial, sans-serif;
}

.clientes-container {
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
.clientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  width: 100%;
  margin-top: 2rem;
  box-sizing: border-box;
}
.tarjeta-cliente {
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
.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.cliente-nombre {
  font-weight: 800;
  color: #22223b;
  font-size: 1.08em;
  letter-spacing: 0.01em;
}
.cliente-tel, .cliente-dir {
  color: #2563eb;
  font-size: 0.98em;
  font-weight: 600;
}
.cliente-actions {
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

.success-msg {
  color: #22c55e;
  font-size: 1.08em;
  margin-top: 1.1rem;
  text-align: center;
  font-weight: 700;
}
.error-msg {
  color: #ef4444;
  font-size: 1.05em;
  margin-left: 5px;
  text-align: center;
  font-weight: 700;
}
.loading-msg {
  color: #2563eb;
  font-size: 1.05em;
  text-align: center;
  font-weight: 700;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  font-size: 1.08rem;
  background: #f8fafc;
  color: #22223b;
  box-shadow: 0 1px 4px rgba(30, 64, 175, 0.04);
}

.clientes-list {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.cliente-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0.7rem;
  border-bottom: 2px solid #e5e7eb;
  transition: background 0.2s;
  background: #f8fafc;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(30, 64, 175, 0.06);
  gap: 1.2rem;
}
.cliente-item:hover {
  background: #e0e7ef;
}
.cliente-info {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.cliente-nombre {
  font-weight: 800;
  color: #22223b;
  font-size: 1.08em;
  letter-spacing: 0.01em;
}
.cliente-tel, .cliente-dir {
  color: #2563eb;
  font-size: 0.98em;
  font-weight: 600;
}
.cliente-actions {
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
.total-clientes {
  color: #64748b;
  font-size: 0.98em;
  margin-left: 1.2rem;
}

@media (max-width: 1100px) {
  .clientes-container {
    flex-direction: column;
    gap: 2rem;
    padding: 1rem 0.5rem;
  }
  .card-formulario, .card-listado {
    max-width: 100%;
    width: 100%;
  }
}

@media (max-width: 800px) {
  html, body {
    width: 100%;
    overflow-x: hidden;
  }
  .clientes-container {
    flex-direction: column;
    gap: 1.2rem;
    padding: 0.5rem 0.2rem;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }
  .card, .card-formulario, .card-listado {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    box-sizing: border-box;
    padding: 1.2rem 0.7rem;
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  }
  .clientes-grid {
    grid-template-columns: 1fr;
    gap: 1.1rem;
    margin-top: 1rem;
    width: 100%;
    box-sizing: border-box;
  }
  .tarjeta-cliente {
    padding: 1rem;
    border-radius: 8px;
    box-sizing: border-box;
  }
  .form-group label {
    font-size: 0.98em;
  }
  .form-actions {
    flex-direction: column;
    gap: 0.7rem;
  }
}
</style> 