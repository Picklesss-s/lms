import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'

// Pinia store to manage the application's student data state
export const useStudentStore = defineStore('student', () => {
  const students = ref<any[]>([])
  const loading = ref(false)

  // Fetches students from the API and updates the state
  async function fetchStudents() {
    loading.value = true
    try {
      students.value = await api.getStudents()
    } finally {
      loading.value = false
    }
  }

  return { students, loading, fetchStudents }
})