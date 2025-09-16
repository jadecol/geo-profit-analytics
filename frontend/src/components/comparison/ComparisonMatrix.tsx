// frontend/src/components/comparison/ComparisonMatrix.tsx
import React from 'react';
import { motion } from 'framer-motion';

interface ComparisonMatrixProps {
  data: any;
  filters: any;
  onFilterChange: (filters: any) => void;
}

const ComparisonMatrix: React.FC<ComparisonMatrixProps> = ({ data, filters, onFilterChange }) => {
  const getScoreColor = (score: number, max: number = 10) => {
    const percentage = score / max;
    if (percentage >= 0.8) return '#4ade80';
    if (percentage >= 0.6) return '#fbbf24';
    if (percentage >= 0.4) return '#fb923c';
    return '#f87171';
  };

  const formatValue = (value: number, type: string) => {
    switch (type) {
      case 'currency':
        return `$${Math.round(value).toLocaleString()}`;
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'score':
        return value.toFixed(1);
      default:
        return value.toFixed(2);
    }
  };

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
        overflowX: 'auto'
      }}
    >
      <h3 style={{ 
        color: 'white', 
        marginBottom: '25px',
        fontSize: '20px',
        fontWeight: '300',
        textAlign: 'center'
      }}>
        Matriz de Comparación
      </h3>

      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'separate',
          borderSpacing: '0 10px'
        }}>
          <thead>
            <tr>
              <th style={{
                color: 'rgba(255, 255, 255, 0.9)',
                textAlign: 'left',
                padding: '15px',
                fontSize: '14px',
                fontWeight: '400',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                Métrica
              </th>
              {data.projects.map((project: any, index: number) => (
                <th key={project.id} style={{
                  color: 'white',
                  textAlign: 'center',
                  padding: '15px',
                  fontSize: '14px',
                  fontWeight: '500',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  minWidth: '150px'
                }}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    {project.name}
                  </motion.div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Métricas Financieras */}
            <tr>
              <td colSpan={data.projects.length + 1} style={{
                color: '#8b5cf6',
                fontSize: '12px',
                padding: '20px 15px 10px',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                💰 Métricas Financieras
              </td>
            </tr>
            
            <tr style={{ background: 'rgba(139, 92, 246, 0.05)' }}>
              <td style={{ color: 'rgba(255, 255, 255, 0.8)', padding: '12px 15px' }}>
                VPN (Valor Presente Neto)
              </td>
              {data.metrics.map((metric: any, index: number) => (
                <td key={index} style={{ textAlign: 'center', padding: '12px 15px' }}>
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    style={{
                      color: metric.financial.npv > 0 ? '#4ade80' : '#f87171',
                      fontSize: '16px',
                      fontWeight: '500'
                    }}
                  >
                    {formatValue(metric.financial.npv, 'currency')}
                  </motion.span>
                </td>
              ))}
            </tr>
            
            <tr style={{ background: 'rgba(139, 92, 246, 0.05)' }}>
              <td style={{ color: 'rgba(255, 255, 255, 0.8)', padding: '12px 15px' }}>
                TIR (Tasa Interna de Retorno)
              </td>
              {data.metrics.map((metric: any, index: number) => (
                <td key={index} style={{ textAlign: 'center', padding: '12px 15px' }}>
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    style={{
                      color: getScoreColor(metric.financial.irr, 0.3),
                      fontSize: '16px',
                      fontWeight: '500'
                    }}
                  >
                    {formatValue(metric.financial.irr, 'percentage')}
                  </motion.span>
                </td>
              ))}
            </tr>

            {/* Métricas Geoespaciales */}
            <tr>
              <td colSpan={data.projects.length + 1} style={{
                color: '#3b82f6',
                fontSize: '12px',
                padding: '20px 15px 10px',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                🗺️ Métricas Geoespaciales
              </td>
            </tr>
            
            <tr style={{ background: 'rgba(59, 130, 246, 0.05)' }}>
              <td style={{ color: 'rgba(255, 255, 255, 0.8)', padding: '12px 15px' }}>
                Puntuación de Ubicación
              </td>
              {data.metrics.map((metric: any, index: number) => (
                <td key={index} style={{ textAlign: 'center', padding: '12px 15px' }}>
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1, type: "spring" }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '60px',
                      height: '60px',
                      borderRadius: '50%',
                      background: `conic-gradient(${getScoreColor(metric.geospatial.location)} ${metric.geospatial.location * 36}deg, rgba(255,255,255,0.1) 0deg)`,
                      boxShadow: `0 0 20px ${getScoreColor(metric.geospatial.location)}40`
                    }}
                  >
                    <div style={{
                      width: '45px',
                      height: '45px',
                      borderRadius: '50%',
                      background: 'rgba(0, 0, 0, 0.8)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: getScoreColor(metric.geospatial.location),
                      fontSize: '14px',
                      fontWeight: 'bold'
                    }}>
                      {metric.geospatial.location.toFixed(1)}
                    </div>
                  </motion.div>
                </td>
              ))}
            </tr>

            {/* Métricas de Sostenibilidad */}
            <tr>
              <td colSpan={data.projects.length + 1} style={{
                color: '#10b981',
                fontSize: '12px',
                padding: '20px 15px 10px',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                🌱 Métricas de Sostenibilidad
              </td>
            </tr>
            
            <tr style={{ background: 'rgba(16, 185, 129, 0.05)' }}>
              <td style={{ color: 'rgba(255, 255, 255, 0.8)', padding: '12px 15px' }}>
                Puntuación de Sostenibilidad
              </td>
              {data.metrics.map((metric: any, index: number) => (
                <td key={index} style={{ textAlign: 'center', padding: '12px 15px' }}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                  >
                    <span style={{
                      color: getScoreColor(metric.sustainability.score),
                      fontSize: '18px',
                      fontWeight: '600'
                    }}>
                      {metric.sustainability.score.toFixed(1)}/10
                    </span>
                    <div style={{
                      width: '100px',
                      height: '6px',
                      background: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${metric.sustainability.score * 10}%` }}
                        transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                        style={{
                          height: '100%',
                          background: getScoreColor(metric.sustainability.score),
                          boxShadow: `0 0 10px ${getScoreColor(metric.sustainability.score)}60`
                        }}
                      />
                    </div>
                  </motion.div>
                </td>
              ))}
            </tr>

            {/* Puntuación General */}
            <tr>
              <td style={{
                color: 'white',
                fontSize: '16px',
                padding: '20px 15px',
                fontWeight: '600',
                background: 'linear-gradient(90deg, rgba(139, 92, 246, 0.2), transparent)'
              }}>
                ⭐ PUNTUACIÓN GENERAL
              </td>
              {data.metrics.map((metric: any, index: number) => (
                <td key={index} style={{ 
                  textAlign: 'center', 
                  padding: '20px 15px',
                  background: 'rgba(139, 92, 246, 0.1)'
                }}>
                  <motion.div
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ 
                      delay: index * 0.1, 
                      type: "spring",
                      stiffness: 200
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '15px 25px',
                      background: `linear-gradient(135deg, ${getScoreColor(metric.overall)}, ${getScoreColor(metric.overall)}80)`,
                      borderRadius: '50px',
                      boxShadow: `0 0 25px ${getScoreColor(metric.overall)}60`,
                      color: 'white',
                      fontSize: '20px',
                      fontWeight: 'bold'
                    }}
                  >
                    {metric.overall.toFixed(1)}
                  </motion.div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default ComparisonMatrix;