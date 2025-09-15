export interface Project {
  id: number;
  name: string;
  description?: string;
  location: string;
  status: string;
  zone_type: string;
  total_area: number;
  terrain_value: number;
  construction_cost_per_m2: number;
  investment_horizon: number;
  npv?: number;
  irr?: number;
  created_at: string;
}

export interface ProjectFormData {
  name: string;
  description: string;
  location: string;
  zone_type: string;
  total_area: number;
  terrain_value: number;
  construction_cost_per_m2: number;
  investment_horizon: number;
}
