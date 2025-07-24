<template>
  <div class="leer-factura-root">
    <h2>Leer Factura (OCR)</h2>
    <form @submit.prevent="enviarImagen">
      <div class="form-group">
        <label>Selecciona una imagen o toma una foto:</label>
        <input type="file" accept="image/*" capture="environment" @change="onFileChange" required />
      </div>
      <div v-if="previewUrl" class="preview">
        <img :src="previewUrl" alt="Vista previa" />
      </div>
      <button type="submit" :disabled="!imagen || cargando">Procesar imagen</button>
    </form>
    <div v-if="cargando" class="cargando">Procesando imagen...</div>
    <div v-if="error" class="mensaje-error">{{ error }}</div>
    <div v-if="textoExtraido" class="resultado-ocr">
      <h3>Texto extraído</h3>
      <textarea v-model="textoEditable" rows="10" style="width:100%"></textarea>
      <button @click="procesarPedidoSugerido">Sugerir pedido</button>
    </div>
    <div v-if="pedidoSugerido.length > 0" class="pedido-sugerido">
      <h3>Pedido sugerido</h3>
      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in pedidoSugerido" :key="idx">
            <td>
              <input v-model="item.nombre" />
            </td>
            <td>
              <input type="number" v-model.number="item.cantidad" min="1" />
            </td>
            <td>
              <button @click="eliminarItem(idx)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="guardarBorrador" :disabled="guardando">Guardar como borrador</button>
      <div v-if="mensaje" class="mensaje-exito">{{ mensaje }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeerFactura',
  data() {
    return {
      imagen: null,
      previewUrl: '',
      cargando: false,
      error: '',
      textoExtraido: '',
      textoEditable: '',
      pedidoSugerido: [],
      guardando: false,
      mensaje: ''
    }
  },
  methods: {
    onFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        this.imagen = file;
        this.previewUrl = URL.createObjectURL(file);
      }
    },
    async enviarImagen() {
      if (!this.imagen) return;
      this.cargando = true;
      this.error = '';
      this.textoExtraido = '';
      this.textoEditable = '';
      this.pedidoSugerido = [];
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const formData = new FormData();
        formData.append('file', this.imagen);
        const res = await fetch(`${apiUrl}/ocr/leer-factura`, {
          method: 'POST',
          body: formData
        });
        if (!res.ok) throw new Error('No se pudo procesar la imagen');
        const data = await res.json();
        this.textoExtraido = data.texto;
        this.textoEditable = data.texto;
      } catch (e) {
        this.error = e.message || 'Error procesando imagen';
      } finally {
        this.cargando = false;
      }
    },
    procesarPedidoSugerido() {
      // Lógica simple: buscar líneas tipo "producto cantidad" (ej: "Jabón 3")
      const lineas = this.textoEditable.split('\n');
      const sugerido = [];
      for (let linea of lineas) {
        linea = linea.trim();
        if (!linea) continue;
        // Buscar patrón: nombre y cantidad al final
        const match = linea.match(/(.+?)\s+(\d+)$/);
        if (match) {
          sugerido.push({ nombre: match[1].trim(), cantidad: parseInt(match[2]) });
        }
      }
      this.pedidoSugerido = sugerido;
    },
    eliminarItem(idx) {
      this.pedidoSugerido.splice(idx, 1);
    },
    async guardarBorrador() {
      if (this.pedidoSugerido.length === 0) return;
      this.guardando = true;
      this.mensaje = '';
      try {
        // Aquí deberías llamar a tu endpoint de crear pedido en estado borrador
        // Por ahora solo mostramos mensaje de éxito
        this.mensaje = 'Pedido guardado como borrador (simulado)';
        // TODO: Integrar con backend para guardar realmente el pedido
      } catch (e) {
        this.error = e.message || 'Error guardando borrador';
      } finally {
        this.guardando = false;
      }
    }
  }
}
</script>

<style scoped>
.leer-factura-root {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.form-group {
  margin-bottom: 1rem;
}
.preview img {
  max-width: 100%;
  max-height: 300px;
  margin-bottom: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.cargando {
  color: #2d8cf0;
  margin-top: 1rem;
}
.mensaje-error {
  color: red;
  margin-top: 1rem;
}
.resultado-ocr {
  margin-top: 2rem;
}
.pedido-sugerido {
  margin-top: 2rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}
.pedido-sugerido table {
  width: 100%;
  border-collapse: collapse;
}
.pedido-sugerido th, .pedido-sugerido td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
}
.mensaje-exito {
  color: green;
  margin-top: 1rem;
}
</style> 