import React, { useState } from 'react';
import { projectService } from '../../services/api';
import { ProjectFormData } from '../../types';

interface ProjectFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

const ProjectForm: React.FC<ProjectFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    location: '',
    zone_type: 'residential',
    total_area: 0,
    terrain_value: 0,
    construction_cost_per_m2: 0,
    investment_horizon: 5
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['total_area', 'terrain_value', 'construction_cost_per_m2', 'investment_horizon'].includes(name) 
        ? Number(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await projectService.createProject(formData);
      alert('Proyecto creado exitosamente');
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creando proyecto');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2>Nuevo Proyecto</h2>
      
      {error && (
        <div style={{ 
          color: 'red', 
          backgroundColor: '#ffebee', 
          padding: '10px', 
          borderRadius: '4px', 
          marginBottom: '20px' 
        }}>
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label>Nombre del Proyecto *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Descripción</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={3}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Ubicación *</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Tipo de Zona *</label>
          <select
            name="zone_type"
            value={formData.zone_type}
            onChange={handleInputChange}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="residential">Residencial</option>
            <option value="commercial">Comercial</option>
            <option value="mixed">Mixto</option>
            <option value="industrial">Industrial</option>
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Área Total (m²) *</label>
          <input
            type="number"
            name="total_area"
            value={formData.total_area}
            onChange={handleInputChange}
            required
            min="1"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Valor del Terreno (USD) *</label>
          <input
            type="number"
            name="terrain_value"
            value={formData.terrain_value}
            onChange={handleInputChange}
            required
            min="1"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Costo de Construcción por m² (USD) *</label>
          <input
            type="number"
            name="construction_cost_per_m2"
            value={formData.construction_cost_per_m2}
            onChange={handleInputChange}
            required
            min="1"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label>Horizonte de Inversión (años) *</label>
          <input
            type="number"
            name="investment_horizon"
            value={formData.investment_horizon}
            onChange={handleInputChange}
            required
            min="1"
            max="30"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div style={{ marginTop: '30px' }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginRight: '10px'
            }}
          >
            {loading ? 'Creando...' : 'Crear Proyecto'}
          </button>
          
          <button
            type="button"
            onClick={onCancel}
            style={{
              backgroundColor: '#f44336',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProjectForm;