<template>
  <div class="app-root">
    <header class="main-header">
      <div class="header-content">
        <span class="logo">Gestor de Pedidos</span>
        <!-- Botón hamburguesa solo visible en móvil -->
        <button class="hamburger" @click="menuAbierto = !menuAbierto" aria-label="Abrir menú" :aria-expanded="menuAbierto">
          <span :class="{ 'open': menuAbierto }"></span>
          <span :class="{ 'open': menuAbierto }"></span>
          <span :class="{ 'open': menuAbierto }"></span>
        </button>
        <!-- Navegación principal -->
        <nav class="nav-bar" :class="{ 'mobile-open': menuAbierto }">
          <button :class="{ active: vista === 'productos' }" @click="cambiarVista('productos')">Productos</button>
          <button :class="{ active: vista === 'clientes' }" @click="cambiarVista('clientes')">Clientes</button>
        </nav>
      </div>
      <!-- Fondo oscuro al abrir menú en móvil -->
      <div v-if="menuAbierto" class="menu-backdrop" @click="menuAbierto = false"></div>
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
      vista: 'productos',
      menuAbierto: false
    }
  },
  methods: {
    cambiarVista(v) {
      this.vista = v
      this.menuAbierto = false // Cierra el menú al navegar
    }
  }
}
</script>