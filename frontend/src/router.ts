import { createRouter, createWebHistory } from 'vue-router'
import StudentDashboard from './views/StudentDashboard.vue'

// Defines the routing for the frontend application
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: StudentDashboard }
  ]
})

export default router