// import axios from 'axios'
import { mockSolutionData, mockSolutionsList } from '../mock/data.js'

// const BASE_URL = 'http://localhost:8001'

// const api = axios.create({
//   baseURL: BASE_URL,
//   timeout: 600000,
//   headers: {
//     'Content-Type': 'application/json'
//   }
// })

// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     console.error('API Error:', error)
//     return Promise.reject(error)
//   }
// )

export const requirementApi = {
  submit(data) {
    // return api.post('/api/requirements', data)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { id: 'mock-requirement-001', ...data } })
      }, 500)
    })
  },
  getById(id) {
    // return api.get(`/api/requirements/${id}`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { id, ...mockSolutionData.intermediate_results.requirement_parser.requirement } })
      }, 300)
    })
  },
  getAll() {
    // return api.get('/api/requirements')
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: [{ id: 'mock-requirement-001', location: '乌兰察布', created_at: new Date().toISOString() }] })
      }, 300)
    })
  }
}

export const solutionApi = {
  getById(id) {
    // return api.get(`/api/solutions/${id}`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: mockSolutionData })
      }, 500)
    })
  },
  getAll() {
    // return api.get('/api/solutions')
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: mockSolutionsList })
      }, 500)
    })
  },
  exportMarkdown(id) {
    // return api.get(`/api/solutions/${id}/export/markdown`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { content: mockSolutionData.final_report } })
      }, 300)
    })
  }
}

export const workflowApi = {
  startDirect(data) {
    // return api.post('/api/workflow/start', data)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { workflow_id: 'mock-workflow-001', requirement_id: 'mock-requirement-001' } })
      }, 800)
    })
  },
  getStatus(workflowId) {
    // return api.get(`/api/workflow/status/${workflowId}`)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { status: 'completed' } })
      }, 300)
    })
  },
  connectStream(workflowId) {
    // return new EventSource(`${BASE_URL}/api/workflow/stream/${workflowId}`)
    // 不返回真实的EventSource，在前端模拟
    return null
  }
}

export const systemApi = {
  getStatus() {
    // return api.get('/api/system/status')
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { status: 'ok', mock_mode: true } })
      }, 200)
    })
  }
}

// export default api
