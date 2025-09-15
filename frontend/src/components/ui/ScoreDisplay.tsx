import React from 'react';
import { motion } from 'framer-motion';

interface ScoreDisplayProps {
  score: number;
  projectLocation: string;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ score, projectLocation }) => {
  return (
    <motion.div
      style={{ display: 'inline-block', position: 'relative' }}
      whileHover="hover"
      initial="initial"
    >
      {/* Puntuación principal */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
        style={{
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '20px',
          padding: '15px 25px',
          textAlign: 'center'
        }}
      >
        <div style={{ color: 'white', fontSize: '12px', opacity: 0.8 }}>Puntuación General</div>
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          style={{ 
            color: score >= 8 ? '#4ade80' : score >= 6 ? '#fbbf24' : score > 0 ? '#f87171' : '#9ca3af',
            fontSize: '28px',
            fontWeight: 'bold',
            textShadow: '0 0 10px currentColor'
          }}
        >
          {score > 0 ? score.toFixed(1) : '0.0'}/10
        </motion.div>
      </motion.div>
      
      {/* Tooltip con hover effect */}
      <motion.div
        variants={{
          initial: { opacity: 0, y: 10, scale: 0.8 },
          hover: { opacity: 1, y: 0, scale: 1 }
        }}
        transition={{ duration: 0.3 }}
        style={{
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(0, 255, 136, 0.1)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0, 255, 136, 0.3)',
          borderRadius: '8px',
          padding: '8px 12px',
          marginTop: '5px',
          fontSize: '12px',
          color: '#00ff88',
          textAlign: 'center',
          zIndex: 1000,
          whiteSpace: 'nowrap'
        }}
      >
        📍 {projectLocation}
        <br />
        <span style={{ opacity: 0.7 }}>
          {score >= 8 ? 'Excelente proyecto' : 
           score >= 6 ? 'Proyecto viable' : 
           score > 0 ? 'Necesita mejoras' : 'Calculando...'}
        </span>
      </motion.div>
    </motion.div>
  );
};

export default ScoreDisplay;