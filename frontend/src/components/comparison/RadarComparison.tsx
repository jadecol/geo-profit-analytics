// frontend/src/components/comparison/RadarComparison.tsx
import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface RadarComparisonProps {
  data: any;
}

const RadarComparison: React.FC<RadarComparisonProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current || !data) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Configurar canvas
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 60;
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Métricas para el radar
    const metrics = [
      { label: 'VPN', key: 'npv', max: 2000000 },
      { label: 'TIR', key: 'irr', max: 0.3 },
      { label: 'Ubicación', key: 'location', max: 10 },
      { label: 'Accesibilidad', key: 'accessibility', max: 10 },
      { label: 'Sostenibilidad', key: 'sustainability', max: 10 },
      { label: 'ROI', key: 'roi', max: 100 }
    ];
    
    const angleStep = (Math.PI * 2) / metrics.length;
    
    // Dibujar grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath();
      for (let j = 0; j <= metrics.length; j++) {
        const angle = j * angleStep - Math.PI / 2;
        const x = centerX + Math.cos(angle) * (radius * i / 5);
        const y = centerY + Math.sin(angle) * (radius * i / 5);
        
        if (j === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    }
    
    // Dibujar líneas radiales
    metrics.forEach((_, index) => {
      const angle = index * angleStep - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(
        centerX + Math.cos(angle) * radius,
        centerY + Math.sin(angle) * radius
      );
      ctx.stroke();
    });
    
    // Dibujar etiquetas
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    metrics.forEach((metric, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + Math.cos(angle) * (radius + 30);
      const y = centerY + Math.sin(angle) * (radius + 30);
      ctx.fillText(metric.label, x, y);
    });
    
    // Colores para cada proyecto
    const colors = [
      'rgba(139, 92, 246, 0.7)',
      'rgba(59, 130, 246, 0.7)',
      'rgba(16, 185, 129, 0.7)',
      'rgba(251, 146, 60, 0.7)'
    ];
    
    // Dibujar datos de cada proyecto
    data.projects.forEach((project: any, projectIndex: number) => {
      const projectMetrics = data.metrics[projectIndex];
      
      ctx.beginPath();
      ctx.strokeStyle = colors[projectIndex];
      ctx.fillStyle = colors[projectIndex].replace('0.7', '0.3');
      ctx.lineWidth = 2;
      
      metrics.forEach((metric, index) => {
        let value = 0;
        
        switch (metric.key) {
          case 'npv':
            value = projectMetrics.financial.npv / metric.max;
            break;
          case 'irr':
            value = projectMetrics.financial.irr / metric.max;
            break;
          case 'location':
            value = projectMetrics.geospatial.location / metric.max;
            break;
          case 'accessibility':
            value = projectMetrics.geospatial.accessibility / metric.max;
            break;
          case 'sustainability':
            value = projectMetrics.sustainability.score / metric.max;
            break;
          case 'roi':
            value = projectMetrics.financial.roi / metric.max;
            break;
        }
        
        value = Math.min(1, Math.max(0, value));
        
        const angle = index * angleStep - Math.PI / 2;
        const x = centerX + Math.cos(angle) * (radius * value);
        const y = centerY + Math.sin(angle) * (radius * value);
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    });
    
  }, [data]);
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '20px',
        padding: '30px'
      }}
    >
      <h3 style={{ 
        color: 'white', 
        marginBottom: '25px',
        fontSize: '20px',
        fontWeight: '300',
        textAlign: 'center'
      }}>
        Análisis Radar Multidimensional
      </h3>
      
      <div style={{ position: 'relative', height: '500px' }}>
        <canvas
          ref={canvasRef}
          style={{
            width: '100%',
            height: '100%',
            background: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.05), transparent)'
          }}
        />
        
        {/* Leyenda */}
        <div style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '10px',
          padding: '15px'
        }}>
          {data.projects.map((project: any, index: number) => (
            <div key={project.id} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '8px'
            }}>
              <div style={{
                width: '20px',
                height: '3px',
                background: [
                  'rgba(139, 92, 246, 0.7)',
                  'rgba(59, 130, 246, 0.7)',
                  'rgba(16, 185, 129, 0.7)',
                  'rgba(251, 146, 60, 0.7)'
                ][index]
              }} />
              <span style={{ color: 'white', fontSize: '12px' }}>
                {project.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default RadarComparison;