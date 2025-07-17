<template>
  <div class="app-root">
    <header class="main-header">
      <div class="header-content">
        <span class="logo">Gestor de Pedidos</span>
        <nav class="nav-bar">
          <button :class="{ active: vista === 'productos' }" @click="vista = 'productos'">Productos</button>
          <button :class="{ active: vista === 'clientes' }" @click="vista = 'clientes'">Clientes</button>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <Productos v-if="vista === 'productos'" />
      <Clientes v-else />
    </main>
  </div>
</template>

<script>
import Productos from './components/Productos.vue'
import Clientes from './components/Clientes.vue'
import './assets/global.css'

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