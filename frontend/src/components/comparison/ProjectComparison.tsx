import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { projectService } from '../../services/api';
import { Project } from '../../types';
import ProjectSelector from './ProjectSelector';
import ComparisonMatrix from './ComparisonMatrix';
import RadarComparison from './RadarComparison';
import RankingTable from './RankingTable';

interface ProjectComparisonProps {
  onBack: () => void;
}

interface ComparisonData {
  projects: Project[];
  metrics: {
    financial: { npv: number; irr: number; roi: number };
    geospatial: { location: number; accessibility: number };
    sustainability: { score: number; carbonFootprint: number };
    overall: number;
  }[];
}

const ProjectComparison: React.FC<ProjectComparisonProps> = ({ onBack }) => {
  const [selectedProjects, setSelectedProjects] = useState<Project[]>([]);
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [viewMode, setViewMode] = useState<'matrix' | 'radar' | 'ranking'>('matrix');
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    minNPV: 0,
    minIRR: 0,
    minSustainability: 0,
    zoneType: 'all'
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectService.getProjects();
      setAllProjects(response.data.items || []);
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const handleProjectSelect = (project: Project) => {
    if (selectedProjects.find(p => p.id === project.id)) {
      setSelectedProjects(selectedProjects.filter(p => p.id !== project.id));
    } else if (selectedProjects.length < 4) {
      setSelectedProjects([...selectedProjects, project]);
    }
  };

  const runComparison = async () => {
    if (selectedProjects.length < 2) {
      alert('Selecciona al menos 2 proyectos para comparar');
      return;
    }

    setLoading(true);
    try {
      // Simular llamada a API con datos mock
      const mockData: ComparisonData = {
        projects: selectedProjects,
        metrics: selectedProjects.map(project => ({
          financial: {
            npv: project.npv || Math.random() * 1000000,
            irr: project.irr || Math.random() * 0.3,
            roi: Math.random() * 50
          },
          geospatial: {
            location: 7 + Math.random() * 3,
            accessibility: 6 + Math.random() * 4
          },
          sustainability: {
            score: 5 + Math.random() * 5,
            carbonFootprint: 1000 + Math.random() * 500
          },
          overall: 6 + Math.random() * 4
        }))
      };
      
      setComparisonData(mockData);
    } catch (error) {
      console.error('Error comparing projects:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
      padding: '0',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Efectos de fondo animados */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 30%, rgba(139, 92, 246, 0.1) 0%, transparent 40%),
          radial-gradient(circle at 80% 70%, rgba(59, 130, 246, 0.1) 0%, transparent 40%),
          radial-gradient(circle at 40% 80%, rgba(147, 51, 234, 0.1) 0%, transparent 40%)
        `,
        animation: 'pulse 8s ease-in-out infinite'
      }} />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '20px 40px',
          position: 'sticky',
          top: 0,
          zIndex: 100
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onBack}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #ff6b6b, #ee5a52)',
                color: 'white',
                border: 'none',
                borderRadius: '50px',
                cursor: 'pointer',
                marginRight: '20px',
                fontSize: '14px',
                fontWeight: '500',
                boxShadow: '0 4px 15px rgba(255, 107, 107, 0.4)'
              }}
            >
              ← Volver
            </motion.button>
            
            <span style={{ color: 'white', fontSize: '24px', fontWeight: '300' }}>
              Comparación de Proyectos
            </span>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            {['matrix', 'radar', 'ranking'].map((mode) => (
              <motion.button
                key={mode}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setViewMode(mode as any)}
                style={{
                  padding: '10px 20px',
                  background: viewMode === mode 
                    ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
                    : 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '25px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  transition: 'all 0.3s ease'
                }}
              >
                {mode === 'matrix' ? '📊 Matriz' : 
                 mode === 'radar' ? '🎯 Radar' : '🏆 Ranking'}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      <div style={{ padding: '40px', position: 'relative', zIndex: 1 }}>
        {/* Selector de Proyectos */}
        <ProjectSelector
          projects={allProjects}
          selectedProjects={selectedProjects}
          onProjectSelect={handleProjectSelect}
          onCompare={runComparison}
          loading={loading}
        />

        {/* Área de Comparación */}
        {comparisonData && (
          <AnimatePresence mode="wait">
            {viewMode === 'matrix' && (
              <ComparisonMatrix
                key="matrix"
                data={comparisonData}
                filters={filters}
                onFilterChange={setFilters}
              />
            )}
            
            {viewMode === 'radar' && (
              <RadarComparison
                key="radar"
                data={comparisonData}
              />
            )}
            
            {viewMode === 'ranking' && (
              <RankingTable
                key="ranking"
                data={comparisonData}
                filters={filters}
              />
            )}
          </AnimatePresence>
        )}
      </div>

      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% { opacity: 0.4; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.05); }
          }
        `
      }} />
    </div>
  );
};

export default ProjectComparison;