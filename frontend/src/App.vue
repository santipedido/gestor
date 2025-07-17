<template>
  <div class="app-container">
    <Productos />
    <Clientes />
  </div>
</template>

<script>
import Productos from './components/Productos.vue'
import Clientes from './components/Clientes.vue'

export default {
  components: {
    Productos,
    Clientes
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

.app-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  box-sizing: border-box;
}

@media (min-width: 900px) {
  .app-container {
    flex-direction: row;
    align-items: flex-start;
    gap: 2.5rem;
  }
}
</style>