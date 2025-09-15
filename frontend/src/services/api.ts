import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const projectService = {
  getProjects: () => api.get('/projects/'),
  getProject: (id: number) => api.get(`/projects/${id}`),
  createProject: (data: any) => api.post('/projects/', data),
  updateProject: (id: number, data: any) => api.put(`/projects/${id}`, data),
  deleteProject: (id: number) => api.delete(`/projects/${id}`)
};

export const analysisService = {
  runFinancialAnalysis: (projectId: number) => 
    api.post(`/analysis/${projectId}/financial`),
  runGeospatialAnalysis: (projectId: number) => 
    api.post(`/analysis/${projectId}/geospatial`),
  runSustainabilityAnalysis: (projectId: number) => 
    api.post(`/analysis/${projectId}/sustainability`)
};
