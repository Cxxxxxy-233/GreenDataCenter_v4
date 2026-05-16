import axios from 'axios'

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const BASE_URL = rawBaseUrl.replace(/\/$/, '')

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
    return Promise.reject(new Error('后端当前未提供 POST /api/requirements，请直接使用 workflowApi.startDirect()'))
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
  },
  exportPdf(id) {
    return api.get(`/api/solutions/${id}/export/pdf`, {
      responseType: 'blob'
    })
  }
}

export const artifactApi = {
  getFileUrl(path, download = false) {
    if (!path) return ''
    const params = new URLSearchParams({ path })
    if (download) params.set('download', '1')
    return `${BASE_URL}/api/artifacts/file?${params.toString()}`
  },
  preview(path, limit = 50) {
    return api.get('/api/artifacts/preview', {
      params: { path, limit }
    })
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
    return new EventSource(`${BASE_URL}/api/workflow/stream/${encodeURIComponent(workflowId)}`)
  }
}

export const systemApi = {
  getStatus() {
    return api.get('/api/system/status')
  }
}

export { BASE_URL }
export default api
