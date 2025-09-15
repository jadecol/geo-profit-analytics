import React, { useState, useEffect } from 'react';
import { projectService } from '../../services/api';
import { Project } from '../../types';

interface ProjectListProps {
  onAnalyze?: (projectId: number, projectName: string) => void;
  onGeospatialAnalysis?: (projectId: number, projectName: string, projectLocation: string) => void;
  onSustainabilityAnalysis?: (projectId: number, projectName: string) => void;
  onIntegratedAnalysis?: (projectId: number, projectName: string, projectLocation: string) => void;
}

//const ProjectList: React.FC<ProjectListProps> = ({ onAnalyze, onGeospatialAnalysis, onSustainabilityAnalysis }) => {
const ProjectList: React.FC<ProjectListProps> = ({ onAnalyze, onGeospatialAnalysis, onSustainabilityAnalysis, onIntegratedAnalysis }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectService.getProjects();
      setProjects(response.data.items || []);
    } catch (err) {
      setError('Error cargando proyectos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(15px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '20px',
      padding: '40px',
      textAlign: 'center',
      color: 'white'
    }}>
      Cargando proyectos...
    </div>
  );

  if (error) return (
    <div style={{
      background: 'rgba(244, 67, 54, 0.1)',
      backdropFilter: 'blur(15px)',
      border: '1px solid rgba(244, 67, 54, 0.3)',
      borderRadius: '20px',
      padding: '40px',
      textAlign: 'center',
      color: 'white'
    }}>
      Error: {error}
    </div>
  );

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(15px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '20px',
      padding: '40px'
    }}>
      <h2 style={{ 
        color: 'white', 
        marginBottom: '30px', 
        fontSize: '24px', 
        fontWeight: '300' 
      }}>
        Proyectos ({projects.length})
      </h2>
      
      {projects.length === 0 ? (
        <div style={{
          textAlign: 'center',
          color: 'rgba(255, 255, 255, 0.8)',
          padding: '60px',
          fontSize: '18px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>📋</div>
          <p>No hay proyectos. ¡Crea tu primer proyecto!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {projects.map(project => (
            <div key={project.id} style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '15px',
              padding: '25px',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1, color: 'white' }}>
                  <h3 style={{ margin: '0 0 15px 0', fontSize: '20px', fontWeight: '400' }}>
                    {project.name}
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', marginBottom: '15px' }}>
                    <p style={{ margin: '5px 0', color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                      📍 {project.location}
                    </p>
                    <p style={{ margin: '5px 0', color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                      📐 {project.total_area.toLocaleString()} m²
                    </p>
                    <p style={{ margin: '5px 0', color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                      💰 ${project.terrain_value.toLocaleString()}
                    </p>
                    <p style={{ margin: '5px 0', color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
                      ⏱️ {project.investment_horizon} años
                    </p>
                  </div>
                  <span style={{ 
                    padding: '6px 12px', 
                    background: project.status === 'draft' ? 'rgba(255, 152, 0, 0.3)' : 'rgba(76, 175, 80, 0.3)',
                    color: 'white',
                    borderRadius: '20px',
                    fontSize: '12px',
                    textTransform: 'uppercase',
                    border: project.status === 'draft' ? '1px solid rgba(255, 152, 0, 0.5)' : '1px solid rgba(76, 175, 80, 0.5)'
                  }}>
                    {project.status}
                  </span>
                </div>
                
                <div style={{ marginLeft: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {onAnalyze && (
                    <button
                      onClick={() => onAnalyze(project.id, project.name)}
                      style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(135deg, #4CAF50, #45a049)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      📊 Financiero
                    </button>
                  )}
                  
                  {onGeospatialAnalysis && (
                    <button
                      onClick={() => onGeospatialAnalysis(project.id, project.name, project.location)}
                      style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(135deg, #FF9800, #F57C00)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      🗺️ Geoespacial
                    </button>
                  )}
                  
                  {onSustainabilityAnalysis && (
                    <button
                      onClick={() => onSustainabilityAnalysis(project.id, project.name)}
                      style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(135deg, #4CAF50, #2E7D32)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      🌱 Sostenibilidad
                    </button>
                  )}

                  {onIntegratedAnalysis && (
                    <button
                      onClick={() => onIntegratedAnalysis(project.id, project.name, project.location)}
                      style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
                      }}
                    >
                      ⚡ Análisis Completo
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectList;