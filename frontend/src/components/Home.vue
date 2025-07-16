<template>
  <div>
    <h1>Home</h1>
    <button @click="probarConexion">Probar conexión con backend</button>
    <p v-if="respuesta">Respuesta: {{ respuesta }}</p>
    <p v-if="error" style="color:red">Error: {{ error }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      respuesta: '',
      error: ''
    }
  },
  methods: {
    async probarConexion() {
      this.respuesta = ''
      this.error = ''
      try {
        const res = await fetch('http://127.0.0.1:8000/')
        if (!res.ok) throw new Error('No responde el backend')
        const data = await res.json()
        this.respuesta = JSON.stringify(data)
      } catch (e) {
        this.error = e.message
      }
    }
  }
}
</script>