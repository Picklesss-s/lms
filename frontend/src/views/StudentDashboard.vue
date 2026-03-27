<template>
  <div class="max-w-6xl mx-auto p-6 mt-10">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800">LMS Dashboard</h1>
    </div>

    <div v-if="studentStore.loading" class="text-center py-10">
      Loading student data...
    </div>

    <div v-else class="grid gap-4">
      <div v-for="student in studentStore.students" :key="student.id"
           class="bg-white p-5 rounded-lg shadow border flex justify-between items-center">
        <div>
          <h2 class="text-lg font-semibold">{{ student.name }}</h2>
          <p class="text-sm text-gray-500">Student ID: {{ student.id }}</p>
        </div>
        <div>
          <span v-if="student.is_at_risk" class="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">⚠️ At-Risk</span>
          <span v-else class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">On Track</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useStudentStore } from '../stores/studentStore'

// Initializes the student store and fetches data on mount
const studentStore = useStudentStore()

onMounted(() => {
  studentStore.fetchStudents()
})
</script>