import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated, config } from '@react-spring/web';

interface FuturisticChartsProps {
  cashFlows?: number[];
  npv?: number;
  irr?: number;
  sustainability?: number;
  location?: number;
  title?: string;
}

const FuturisticCharts: React.FC<FuturisticChartsProps> = ({
  cashFlows = [],
  npv = 0,
  irr = 0,
  sustainability = 0,
  location = 0,
  title = "Análisis de Proyecto"
}) => {
  const [activeChart, setActiveChart] = useState(0);
  const [animatedValues, setAnimatedValues] = useState({
    npv: 0,
    irr: 0,
    sustainability: 0,
    location: 0
  });

  // Animaciones con react-spring
  const npvSpring = useSpring({
    value: animatedValues.npv,
    config: config.wobbly,
    delay: 200
  });

  const irrSpring = useSpring({
    value: animatedValues.irr,
    config: config.gentle,
    delay: 400
  });

  const sustainabilitySpring = useSpring({
    rotation: (animatedValues.sustainability / 10) * 360,
    config: config.slow,
    delay: 600
  });

  const locationSpring = useSpring({
    scale: animatedValues.location > 7 ? 1.2 : animatedValues.location > 5 ? 1.1 : 1,
    config: config.wobbly,
    delay: 800
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValues({
        npv: npv,
        irr: irr * 100,
        sustainability: sustainability,
        location: location
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [npv, irr, sustainability, location]);

  // Componente de gráfico CSS puro MEJORADO para flujo de caja
  const CSSCashFlowChart = () => {
    if (cashFlows.length === 0) {
      return (
        <div style={{ 
          height: 300, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: '#ffffff',
          opacity: 0.7
        }}>
          Sin datos de flujo de caja
        </div>
      );
    }

    const maxValue = Math.max(...cashFlows.map(Math.abs));

    return (
      <div style={{ height: 300, padding: '20px', position: 'relative' }}>
        {/* Líneas de fondo futuristas */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px),
            linear-gradient(0deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
          opacity: 0.3
        }} />
        
        <div style={{ 
          display: 'flex', 
          alignItems: 'end', 
          height: '100%', 
          gap: '6px',
          justifyContent: 'space-around',
          position: 'relative',
          zIndex: 1
        }}>
          {cashFlows.slice(0, 12).map((flow, index) => {
            const height = Math.abs(flow) / maxValue * 180;
            const isPositive = flow >= 0;
            
            return (
              <motion.div
                key={index}
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: height, opacity: 1 }}
                transition={{ 
                  delay: index * 0.15, 
                  duration: 0.8,
                  type: "spring",
                  stiffness: 100
                }}
                style={{
                  background: isPositive 
                    ? 'linear-gradient(to top, #00ff88, #00cc66, #88ff00)'
                    : 'linear-gradient(to top, #ff4444, #cc2222, #ff6666)',
                  width: '24px',
                  borderRadius: '4px',
                  position: 'relative',
                  transformOrigin: 'bottom',
                  marginTop: isPositive ? 'auto' : 0,
                  marginBottom: isPositive ? 0 : 'auto',
                  boxShadow: `0 0 20px ${isPositive ? '#00ff88' : '#ff4444'}60`,
                  border: `1px solid ${isPositive ? '#00ff88' : '#ff4444'}`,
                }}
                whileHover={{ 
                  scale: 1.1,
                  boxShadow: `0 0 30px ${isPositive ? '#00ff88' : '#ff4444'}90`,
                  filter: 'brightness(1.2)'
                }}
                title={`Mes ${index + 1}: $${flow.toLocaleString()}`}
              >
                {/* Efecto de brillo interno */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '30%',
                  background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0.3), transparent)',
                  borderRadius: '4px 4px 0 0'
                }} />
                
                {/* Valor en el hover */}
                <motion.div
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(0, 0, 0, 0.9)',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    fontSize: '10px',
                    whiteSpace: 'nowrap',
                    border: `1px solid ${isPositive ? '#00ff88' : '#ff4444'}`,
                    marginBottom: '5px'
                  }}
                >
                  ${(flow / 1000).toFixed(0)}K
                </motion.div>
              </motion.div>
            );
          })}
        </div>
        
        {/* Etiquetas del eje X futuristas */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-around', 
          marginTop: '15px',
          fontSize: '10px',
          color: '#00ff8880',
          fontWeight: '500',
          textShadow: '0 0 5px #00ff8850'
        }}>
          {cashFlows.slice(0, 12).map((_, index) => (
            <motion.span 
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 + 1 }}
            >
              M{index + 1}
            </motion.span>
          ))}
        </div>
      </div>
    );
  };

  // Componente de gráfico radial CSS puro MEJORADO
  const CSSRadialChart = () => {
    const metrics = [
      { name: 'VPN', value: npv > 0 ? 85 : 15, color: '#00ff88' },
      { name: 'TIR', value: irr > 0.15 ? 90 : irr > 0.12 ? 70 : 30, color: '#0088ff' },
      { name: 'Sostenibilidad', value: sustainability * 10, color: '#88ff00' },
      { name: 'Ubicación', value: location * 10, color: '#ff8800' }
    ];

    return (
      <div style={{ 
        height: 300, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        gap: '30px',
        flexWrap: 'wrap'
      }}>
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              delay: index * 0.2, 
              type: "spring", 
              stiffness: 200,
              damping: 15
            }}
            whileHover={{
              scale: 1.1,
              rotate: 5,
              transition: { duration: 0.2 }
            }}
            style={{ textAlign: 'center' }}
          >
            <div style={{ 
              width: 90, 
              height: 90, 
              borderRadius: '50%',
              background: `conic-gradient(${metric.color} ${metric.value * 3.6}deg, rgba(255,255,255,0.1) 0deg)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              margin: '0 auto 10px',
              boxShadow: `0 0 20px ${metric.color}40`
            }}>
              <div style={{
                width: 65,
                height: 65,
                borderRadius: '50%',
                background: 'rgba(0,0,0,0.9)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: metric.color,
                fontSize: '16px',
                fontWeight: 'bold',
                textShadow: `0 0 10px ${metric.color}`
              }}>
                {metric.value.toFixed(0)}%
              </div>
            </div>
            <div style={{ 
              color: '#ffffff', 
              fontSize: '12px',
              fontWeight: '500',
              textShadow: '0 0 5px rgba(255, 255, 255, 0.5)'
            }}>
              {metric.name}
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  const charts = [
    {
      name: 'Flujo de Caja',
      component: <CSSCashFlowChart />
    },
    {
      name: 'Métricas Clave',
      component: <CSSRadialChart />
    }
  ];

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(20, 20, 40, 0.9))',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(0, 255, 136, 0.3)',
      borderRadius: '20px',
      padding: '30px',
      margin: '20px 0',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 136, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(136, 255, 0, 0.1) 0%, transparent 50%)
          `,
          animation: 'pulse 4s ease-in-out infinite'
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ position: 'relative', zIndex: 1 }}
      >
        <h3 style={{
          color: '#00ff88',
          fontSize: '24px',
          fontWeight: '300',
          marginBottom: '30px',
          textAlign: 'center',
          textShadow: '0 0 10px rgba(0, 255, 136, 0.5)'
        }}>
          {title}
        </h3>

        {/* Métricas animadas MEJORADAS */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <motion.div
            whileHover={{ scale: 1.05 }}
            style={{
              background: 'rgba(0, 255, 136, 0.1)',
              border: '1px solid rgba(0, 255, 136, 0.3)',
              borderRadius: '15px',
              padding: '20px',
              textAlign: 'center'
            }}
          >
            <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px', marginBottom: '5px' }}>
              VPN
            </div>
            <animated.div style={{
              color: '#00ff88',
              fontSize: '20px',
              fontWeight: 'bold',
              textShadow: '0 0 10px rgba(0, 255, 136, 0.5)'
            }}>
              {npvSpring.value.to((val: number) => `$${Math.round(val).toLocaleString()}`)}
            </animated.div>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            style={{
              background: 'rgba(0, 136, 255, 0.1)',
              border: '1px solid rgba(0, 136, 255, 0.3)',
              borderRadius: '15px',
              padding: '20px',
              textAlign: 'center'
            }}
          >
            <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px', marginBottom: '5px' }}>
              TIR
            </div>
            <animated.div style={{
              color: '#0088ff',
              fontSize: '20px',
              fontWeight: 'bold',
              textShadow: '0 0 10px rgba(0, 136, 255, 0.5)'
            }}>
              {irrSpring.value.to((val: number) => `${val.toFixed(1)}%`)}
            </animated.div>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            style={{
              background: 'rgba(136, 255, 0, 0.1)',
              border: '1px solid rgba(136, 255, 0, 0.3)',
              borderRadius: '15px',
              padding: '20px',
              textAlign: 'center'
            }}
          >
            <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px', marginBottom: '5px' }}>
              Sostenibilidad
            </div>
            <animated.div
              style={{
                color: '#88ff00',
                fontSize: '20px',
                fontWeight: 'bold',
                textShadow: '0 0 10px rgba(136, 255, 0, 0.5)',
                display: 'inline-block',
                transformOrigin: 'center',
                transform: sustainabilitySpring.rotation.to((r: number) => `rotate(${r}deg)`)
              }}
            >
              {sustainability.toFixed(1)}/10
            </animated.div>
          </motion.div>

          <animated.div
            style={{
              background: 'rgba(255, 136, 0, 0.1)',
              border: '1px solid rgba(255, 136, 0, 0.3)',
              borderRadius: '15px',
              padding: '20px',
              textAlign: 'center',
              transform: locationSpring.scale.to((s: number) => `scale(${s})`)
            }}
          >
            <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px', marginBottom: '5px' }}>
              Ubicación
            </div>
            <div style={{
              color: '#ff8800',
              fontSize: '20px',
              fontWeight: 'bold',
              textShadow: '0 0 10px rgba(255, 136, 0, 0.5)'
            }}>
              {location.toFixed(1)}/10
            </div>
          </animated.div>
        </div>

        {/* Navegación de gráficos */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '10px',
          marginBottom: '20px'
        }}>
          {charts.map((chart, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveChart(index)}
              style={{
                padding: '8px 16px',
                background: activeChart === index 
                  ? 'linear-gradient(135deg, #00ff88, #00cc66)'
                  : 'rgba(255, 255, 255, 0.1)',
                color: activeChart === index ? '#000' : '#fff',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '20px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
            >
              {chart.name}
            </motion.button>
          ))}
        </div>

        {/* Gráficos animados */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeChart}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.5 }}
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '15px',
              padding: '20px'
            }}
          >
            {charts[activeChart].component}
          </motion.div>
        </AnimatePresence>
      </motion.div>

      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
          }
        `
      }} />
    </div>
  );
};

export default FuturisticCharts;