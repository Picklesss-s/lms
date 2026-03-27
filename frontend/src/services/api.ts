const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client for interacting with the Backend Server
export const api = {
  // Fetches the list of students and their risk status
  async getStudents() {
    const response = await fetch(`${API_URL}/students`);
    if (!response.ok) throw new Error('Failed to fetch students');
    return await response.json();
  },

  // Triggers the backend ML pipeline to sync data from the LMS
  async syncLMSData() {
    const response = await fetch(`${API_URL}/sync`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer instructor-super-secret-token'
      }
    });
    if (!response.ok) throw new Error('Sync failed');
    return await response.json();
  }
};