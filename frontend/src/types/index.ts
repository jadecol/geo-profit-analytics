export interface Project {
  id: string;
  name: string;
  location: {
    lat: number;
    lng: number;
  };
  status: 'active' | 'completed' | 'planned';
}

export interface AnalysisResult {
  projectId: string;
  profitability: number;
  sustainability: number;
  risk: number;
}
