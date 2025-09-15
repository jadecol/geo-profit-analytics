import React, { useState, useEffect } from 'react';
import { projectService } from '../../services/api';
import { Project } from '../../types';

interface DashboardProps {
  onNavigate: (page: string, data?: any) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState({
    totalProjects: 0,
    avgNPV: 0,
    avgIRR: 0,
    successRate: 0
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await projectService.getProjects();
      const projectsData: Project[] = response.data.items || [];
      setProjects(projectsData);
      
      const totalProjects = projectsData.length;
      const projectsWithNPV = projectsData.filter((p: Project) => p.npv && p.npv > 0);
      const avgNPV = projectsWithNPV.length > 0 
        ? projectsWithNPV.reduce((sum: number, p: Project) => sum + (p.npv || 0), 0) / projectsWithNPV.length 
        : 0;
      const successRate = totalProjects > 0 ? (projectsWithNPV.length / totalProjects) * 100 : 0;
      
      setStats({
        totalProjects,
        avgNPV,
        avgIRR: 24.5,
        successRate
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '0',
      margin: '0'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '20px 40px',
        color: 'white'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ 
            margin: 0, 
            fontSize: '28px', 
            fontWeight: '300',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            GeoProfit Analytics
          </h1>
          <div style={{ fontSize: '14px', opacity: 0.8 }}>
            Dashboard Principal
          </div>
        </div>
      </div>

      <div style={{ padding: '40px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '30px',
          marginBottom: '40px'
        }}>
          {[
            { 
              title: 'Proyectos Totales', 
              value: stats.totalProjects.toString(), 
              color: 'rgba(76, 175, 80, 0.2)',
              border: 'rgba(76, 175, 80, 0.3)'
            },
            { 
              title: 'VPN Promedio', 
              value: `$${Math.round(stats.avgNPV).toLocaleString()}`, 
              color: 'rgba(33, 150, 243, 0.2)',
              border: 'rgba(33, 150, 243, 0.3)'
            },
            { 
              title: 'TIR Promedio', 
              value: `${stats.avgIRR.toFixed(1)}%`, 
              color: 'rgba(255, 152, 0, 0.2)',
              border: 'rgba(255, 152, 0, 0.3)'
            },
            { 
              title: 'Tasa de Éxito', 
              value: `${stats.successRate.toFixed(0)}%`, 
              color: 'rgba(156, 39, 176, 0.2)',
              border: 'rgba(156, 39, 176, 0.3)'
            }
          ].map((stat, index) => (
            <div key={index} style={{
              background: `linear-gradient(145deg, ${stat.color}, rgba(255, 255, 255, 0.1))`,
              backdropFilter: 'blur(15px)',
              border: `1px solid ${stat.border}`,
              borderRadius: '20px',
              padding: '30px',
              color: 'white',
              textAlign: 'center',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)';
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
            }}>
              <h3 style={{ 
                margin: '0 0 15px 0', 
                fontSize: '16px', 
                fontWeight: '300',
                opacity: 0.9
              }}>
                {stat.title}
              </h3>
              <p style={{ 
                margin: 0, 
                fontSize: '32px', 
                fontWeight: '600',
                textShadow: '0 2px 8px rgba(0,0,0,0.3)'
              }}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(15px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '20px',
          padding: '40px',
          marginBottom: '40px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{ 
            color: 'white', 
            marginBottom: '30px', 
            fontSize: '24px', 
            fontWeight: '300',
            textAlign: 'center'
          }}>
            Acciones Principales
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {[
              {
                title: 'Nuevo Proyecto',
                description: 'Crear y configurar un nuevo proyecto de análisis',
                action: () => onNavigate('newProject'),
                gradient: 'linear-gradient(135deg, #4CAF50, #45a049)',
                icon: '+'
              },
              {
                title: 'Ver Proyectos',
                description: 'Explorar y gestionar proyectos existentes',
                action: () => onNavigate('projects'),
                gradient: 'linear-gradient(135deg, #2196F3, #1976D2)',
                icon: '📋'
              },
              {
                title: 'Análisis Avanzado',
                description: 'Herramientas de análisis geoespacial y sostenibilidad',
                action: () => onNavigate('advanced'),
                gradient: 'linear-gradient(135deg, #FF9800, #F57C00)',
                icon: '🔬'
              }
            ].map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                style={{
                  background: action.gradient,
                  border: 'none',
                  borderRadius: '15px',
                  padding: '25px',
                  color: 'white',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 6px 20px rgba(0, 0, 0, 0.2)',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.2)';
                }}
              >
                <div style={{ fontSize: '24px', marginBottom: '10px' }}>{action.icon}</div>
                <h3 style={{ margin: '0 0 10px 0', fontSize: '18px' }}>{action.title}</h3>
                <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>{action.description}</p>
              </button>
            ))}
          </div>
        </div>

        {projects.length > 0 && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{ 
              color: 'white', 
              marginBottom: '30px', 
              fontSize: '24px', 
              fontWeight: '300'
            }}>
              Proyectos Recientes
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {projects.slice(0, 3).map((project: Project) => (
                <div
                  key={project.id}
                  style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '12px',
                    padding: '20px',
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => onNavigate('analysis', { projectId: project.id, projectName: project.name })}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                    e.currentTarget.style.transform = 'translateX(5px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ margin: '0 0 5px 0', fontSize: '18px' }}>{project.name}</h3>
                      <p style={{ margin: 0, fontSize: '14px', opacity: 0.8 }}>{project.location}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '14px', opacity: 0.8 }}>
                        {project.total_area.toLocaleString()} m²
                      </div>
                      <div style={{ 
                        fontSize: '12px', 
                        padding: '4px 8px', 
                        background: 'rgba(76, 175, 80, 0.3)',
                        borderRadius: '12px',
                        marginTop: '5px'
                      }}>
                        {project.status}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;