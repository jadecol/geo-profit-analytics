// frontend/src/services/api.ts
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

export const comparisonService = {
  compareProjects: (projectIds: number[]) => 
    api.post('/projects/compare', projectIds),
  
  getProjectRankings: (criteria: string = 'overall', limit: number = 10) =>
    api.get('/projects/ranking', { params: { criteria, limit } }),
  
  exportComparison: (projectIds: number[], format: 'pdf' | 'excel' | 'json') =>
    api.post('/projects/compare/export', { projectIds, format }, { responseType: 'blob' })
};
