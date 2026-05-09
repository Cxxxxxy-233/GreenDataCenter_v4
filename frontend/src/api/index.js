import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const requirementApi = {
  submit(data) {
    return api.post('/api/requirements', data)
  },
  getById(id) {
    return api.get(`/api/requirements/${id}`)
  },
  getAll() {
    return api.get('/api/requirements')
  }
}

export const solutionApi = {
  getById(id) {
    return api.get(`/api/solutions/${id}`)
  },
  getAll() {
    return api.get('/api/solutions')
  },
  exportMarkdown(id) {
    return api.get(`/api/solutions/${id}/export/markdown`)
  }
}

export const workflowApi = {
  startDirect(data) {
    return api.post('/api/workflow/start', data)
  },
  getStatus(workflowId) {
    return api.get(`/api/workflow/status/${workflowId}`)
  },
  connectStream(workflowId) {
    return new EventSource(`${BASE_URL}/api/workflow/stream/${workflowId}`)
  }
}

export const systemApi = {
  getStatus() {
    return api.get('/api/system/status')
  }
}

export default api
