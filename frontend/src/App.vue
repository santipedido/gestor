<template>
  <div>
    <!-- Deploy test - {{ new Date().toISOString() }} -->
    <nav class="nav-bar">
      <button :class="{ active: vista === 'productos' }" @click="vista = 'productos'">Productos</button>
      <button :class="{ active: vista === 'clientes' }" @click="vista = 'clientes'">Clientes</button>
    </nav>
    <Productos v-if="vista === 'productos'" />
    <Clientes v-else />
  </div>
</template>

<script>
import Productos from './components/Productos.vue'
import Clientes from './components/Clientes.vue'

export default {
  components: {
    Productos,
    Clientes
  },
  data() {
    return {
      vista: 'productos'
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, #app {
  font-family: 'Poppins', 'Inter', 'Segoe UI', Arial, sans-serif;
}
.nav-bar {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 0 1.5rem 1rem;
  background: #f7fafd;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 2rem;
}
.nav-bar button {
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2980b9;
  cursor: pointer;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  transition: background 0.2s;
}
.nav-bar button.active, .nav-bar button:hover {
  background: #2980b9;
  color: #fff;
}
</style>