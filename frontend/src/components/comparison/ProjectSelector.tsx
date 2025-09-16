// frontend/src/components/comparison/ProjectSelector.tsx
import React from 'react';
import { motion } from 'framer-motion';
import { Project } from '../../types';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProjects: Project[];
  onProjectSelect: (project: Project) => void;
  onCompare: () => void;
  loading: boolean;
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({
  projects,
  selectedProjects,
  onProjectSelect,
  onCompare,
  loading
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '20px',
        padding: '30px',
        marginBottom: '30px'
      }}
    >
      <h3 style={{ 
        color: 'white', 
        marginBottom: '20px',
        fontSize: '18px',
        fontWeight: '300'
      }}>
        Selecciona proyectos para comparar (máximo 4)
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
        gap: '15px',
        marginBottom: '25px'
      }}>
        {projects.map((project) => {
          const isSelected = selectedProjects.find(p => p.id === project.id);
          const canSelect = selectedProjects.length < 4 || isSelected;
          
          return (
            <motion.div
              key={project.id}
              whileHover={canSelect ? { scale: 1.02 } : {}}
              whileTap={canSelect ? { scale: 0.98 } : {}}
              onClick={() => canSelect && onProjectSelect(project)}
              style={{
                background: isSelected 
                  ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(147, 51, 234, 0.2))'
                  : 'rgba(255, 255, 255, 0.05)',
                border: `2px solid ${isSelected ? '#8b5cf6' : 'rgba(255, 255, 255, 0.1)'}`,
                borderRadius: '15px',
                padding: '20px',
                cursor: canSelect ? 'pointer' : 'not-allowed',
                opacity: canSelect ? 1 : 0.5,
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    width: '30px',
                    height: '30px',
                    background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '18px',
                    boxShadow: '0 0 15px rgba(139, 92, 246, 0.5)'
                  }}
                >
                  ✓
                </motion.div>
              )}
              
              <h4 style={{ 
                color: 'white', 
                margin: '0 0 10px 0',
                fontSize: '16px'
              }}>
                {project.name}
              </h4>
              
              <div style={{ 
                color: 'rgba(255, 255, 255, 0.7)', 
                fontSize: '12px',
                display: 'flex',
                flexDirection: 'column',
                gap: '5px'
              }}>
                <span>📍 {project.location}</span>
                <span>📐 {project.total_area.toLocaleString()} m²</span>
                {project.npv && (
                  <span style={{ color: project.npv > 0 ? '#4ade80' : '#f87171' }}>
                    💰 VPN: ${Math.round(project.npv).toLocaleString()}
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      <div style={{ textAlign: 'center' }}>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onCompare}
          disabled={selectedProjects.length < 2 || loading}
          style={{
            padding: '15px 40px',
            background: selectedProjects.length >= 2 
              ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
              : 'rgba(100, 100, 100, 0.3)',
            color: 'white',
            border: 'none',
            borderRadius: '50px',
            cursor: selectedProjects.length >= 2 ? 'pointer' : 'not-allowed',
            fontSize: '16px',
            fontWeight: '500',
            boxShadow: selectedProjects.length >= 2 
              ? '0 6px 20px rgba(139, 92, 246, 0.4)'
              : 'none',
            transition: 'all 0.3s ease'
          }}
        >
          {loading ? 'Comparando...' : 
           `Comparar ${selectedProjects.length} Proyectos`}
        </motion.button>
        
        {selectedProjects.length < 2 && (
          <p style={{ 
            color: 'rgba(255, 255, 255, 0.5)', 
            fontSize: '12px',
            marginTop: '10px'
          }}>
            Selecciona al menos 2 proyectos para comparar
          </p>
        )}
      </div>
    </motion.div>
  );
};

export default ProjectSelector;