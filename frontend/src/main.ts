import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// Mounts the Vue application with Router and Pinia
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')