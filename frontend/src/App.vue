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

.app-root {
  min-height: 100vh;
  background: #f7fafd;
  font-family: 'Poppins', 'Inter', 'Segoe UI', Arial, sans-serif;
}

.main-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  padding: 0;
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.7rem 1.5rem;
}
.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.01em;
}
.nav-bar {
  display: flex;
  gap: 1.2rem;
}
.nav-bar button {
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
  letter-spacing: 0.01em;
}
.nav-bar button.active, .nav-bar button:hover {
  background: #2563eb;
  color: #fff;
}

.main-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1rem 2rem 1rem;
  box-sizing: border-box;
}

@media (max-width: 700px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 1rem 1rem 0.5rem 1rem;
  }
  .main-content {
    padding: 1.2rem 0.3rem 1.5rem 0.3rem;
  }
  .logo {
    font-size: 1.15rem;
  }
  .nav-bar button {
    font-size: 1rem;
    padding: 0.5rem 1.1rem;
  }
}
</style>