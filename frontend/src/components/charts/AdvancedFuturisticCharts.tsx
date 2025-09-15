import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSpring, animated, config } from "@react-spring/web";

interface AdvancedFuturisticChartsProps {
  cashFlows?: number[];
  npv?: number;
  irr?: number;
  sustainability?: number;
  location?: number;
  title?: string;
}

const AdvancedFuturisticCharts: React.FC<AdvancedFuturisticChartsProps> = ({
  cashFlows = [],
  npv = 0,
  irr = 0,
  sustainability = 0,
  location = 0,
  title = "Análisis de Proyecto",
}) => {
  const [activeChart, setActiveChart] = useState(0);
  const [animatedValues, setAnimatedValues] = useState({
    npv: 0,
    irr: 0,
    sustainability: 0,
    location: 0,
  });

  // RESTAURAR: Estado para el efecto hover del encabezado
  const [headerVisible, setHeaderVisible] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // RESTAURAR: Efecto hover del encabezado
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleMouseEnter = () => setHeaderVisible(true);
    const handleMouseLeave = () => setHeaderVisible(false);

    container.addEventListener("mouseenter", handleMouseEnter);
    container.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      container.removeEventListener("mouseenter", handleMouseEnter);
      container.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  const npvSpring = useSpring({
    value: animatedValues.npv,
    config: config.wobbly,
    delay: 200,
  });

  const irrSpring = useSpring({
    value: animatedValues.irr,
    config: config.gentle,
    delay: 400,
  });

  const sustainabilitySpring = useSpring({
    value: animatedValues.sustainability,
    config: config.gentle,
    delay: 600,
  });

  const locationSpring = useSpring({
    value: animatedValues.location,
    config: config.gentle,
    delay: 800,
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValues({
        npv: npv,
        irr: irr * 100,
        sustainability: sustainability,
        location: location,
      });
    }, 300);

    return () => clearTimeout(timer);
  }, [npv, irr, sustainability, location]);

  // Gráfico de flujo de caja con eje Y restaurado
  const CSSCashFlowChart = () => {
    if (cashFlows.length === 0) {
      return (
        <div
          style={{
            height: 300,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            opacity: 0.7,
            fontSize: "16px",
          }}
        >
          Sin datos de flujo de caja disponibles
        </div>
      );
    }

    const maxValue = Math.max(...cashFlows.map(Math.abs));
    const maxAbsValue = Math.max(...cashFlows.map(Math.abs));

    return (
      <div
        style={{
          height: 340,
          padding: "20px",
          position: "relative",
          background:
            "linear-gradient(135deg, rgba(0, 20, 40, 0.9), rgba(0, 40, 80, 0.7))",
          borderRadius: "15px",
          border: "1px solid rgba(0, 255, 255, 0.3)",
          boxShadow:
            "0 0 30px rgba(0, 255, 255, 0.2), inset 0 0 20px rgba(0, 255, 255, 0.1)",
          overflow: "hidden",
        }}
      >
        {/* Efectos de fondo */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
            radial-gradient(circle at 20% 30%, rgba(0, 255, 255, 0.1) 0%, transparent 20%),
            radial-gradient(circle at 80% 70%, rgba(0, 255, 136, 0.1) 0%, transparent 20%),
            radial-gradient(circle at 40% 80%, rgba(0, 136, 255, 0.1) 0%, transparent 20%)
          `,
            opacity: 0.6,
            zIndex: 0,
          }}
        />

        {/* RESTAURAR: Eje Y con valores */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 60,
            width: "40px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "10px 5px",
            color: "#00ddff",
            fontSize: "10px",
            fontWeight: "600",
            textShadow: "0 0 5px rgba(0, 221, 255, 0.7)",
            zIndex: 2,
          }}
        >
          <span>${maxAbsValue.toLocaleString()}</span>
          <span>${(maxAbsValue / 2).toLocaleString()}</span>
          <span>$0</span>
          <span>-${(maxAbsValue / 2).toLocaleString()}</span>
          <span>-${maxAbsValue.toLocaleString()}</span>
        </div>

        {/* Grid de fondo sin líneas punteadas */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 40,
            right: 0,
            bottom: 60,
            backgroundImage: `
            linear-gradient(to right, rgba(0, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 255, 255, 0.1) 1px, transparent 1px)
          `,
            backgroundSize: "8.33% 20%",
            opacity: 0.3,
            zIndex: 1,
          }}
        />

        <div
          style={{
            display: "flex",
            alignItems: "end",
            height: "calc(100% - 60px)",
            gap: "8px",
            justifyContent: "space-around",
            position: "relative",
            zIndex: 2,
            marginLeft: "40px",
            marginTop: "10px",
          }}
        >
          {cashFlows.slice(0, 12).map((flow, index) => {
            const height = (Math.abs(flow) / maxValue) * 200;
            const isPositive = flow >= 0;

            return (
              <motion.div
                key={index}
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: height, opacity: 1 }}
                transition={{
                  delay: index * 0.1,
                  duration: 0.8,
                  type: "spring",
                  stiffness: 120,
                }}
                style={{
                  background: isPositive
                    ? "linear-gradient(to top, #00ff88 0%, #00ddff 50%, #0077ff 100%)"
                    : "linear-gradient(to top, #ff0066 0%, #ff4444 50%, #ff8800 100%)",
                  width: "22px",
                  borderRadius: "6px 6px 0 0",
                  position: "relative",
                  transformOrigin: "bottom",
                  marginTop: isPositive ? "auto" : 0,
                  marginBottom: isPositive ? 0 : "auto",
                  boxShadow: `
                    0 0 15px ${isPositive ? "#00ff88" : "#ff4444"}80,
                    inset 0 -5px 10px ${
                      isPositive
                        ? "rgba(0, 255, 136, 0.5)"
                        : "rgba(255, 68, 68, 0.5)"
                    }
                  `,
                  border: `1px solid ${isPositive ? "#00ff88" : "#ff4444"}`,
                  overflow: "hidden",
                }}
                whileHover={{
                  scale: 1.15,
                  boxShadow: `0 0 25px ${isPositive ? "#00ff88" : "#ff4444"}`,
                  filter: "brightness(1.5)",
                }}
                title={`Mes ${index + 1}: $${flow.toLocaleString()}`}
              >
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: "30%",
                    background:
                      "linear-gradient(to bottom, rgba(255, 255, 255, 0.4), transparent)",
                    borderRadius: "6px 6px 0 0",
                  }}
                />
              </motion.div>
            );
          })}
        </div>

        {/* Línea base */}
        <div
          style={{
            position: "absolute",
            bottom: "60px",
            left: 40,
            right: 0,
            height: "1px",
            background: "rgba(0, 255, 255, 0.7)",
            boxShadow: "0 0 10px rgba(0, 255, 255, 0.5)",
          }}
        />

        {/* Etiquetas del eje X */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            marginTop: "15px",
            fontSize: "10px",
            color: "#00ddff",
            fontWeight: "600",
            textShadow: "0 0 5px rgba(0, 221, 255, 0.7)",
            position: "relative",
            zIndex: 2,
            marginLeft: "40px",
            paddingRight: "40px",
          }}
        >
          {cashFlows.slice(0, 12).map((_, index) => (
            <span
              key={index}
              style={{
                backgroundColor: "rgba(0, 0, 0, 0.7)",
                padding: "2px 5px",
                borderRadius: "4px",
              }}
            >
              M{index + 1}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Gráfico radial con valores corregidos
  const CSSRadialChart = () => {
    const metrics = [
      {
        name: "VPN",
        value: npv > 0 ? Math.min(95, 75) : Math.max(5, 25),
        color: "#00ff88",
      },
      {
        name: "TIR",
        value: Math.min(95, Math.max(5, irr * 400)),
        color: "#0088ff",
      },
      {
        name: "Sostenibilidad",
        value: sustainability * 10,
        color: "#88ff00",
      },
      {
        name: "Ubicación",
        value: location * 10,
        color: "#ff8800",
      },
    ];

    return (
      <div
        style={{
          height: 300,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "30px",
          flexWrap: "wrap",
          position: "relative",
        }}
      >
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              delay: index * 0.2,
              type: "spring",
              stiffness: 200,
            }}
            whileHover={{ scale: 1.1 }}
            style={{ textAlign: "center", position: "relative", zIndex: 1 }}
          >
            <div
              style={{
                width: 90,
                height: 90,
                borderRadius: "50%",
                background: `conic-gradient(${metric.color} ${
                  metric.value * 3.6
                }deg, rgba(255,255,255,0.1) 0deg)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 10px",
                boxShadow: `0 0 20px ${metric.color}40`,
              }}
            >
              <div
                style={{
                  width: 65,
                  height: 65,
                  borderRadius: "50%",
                  background: "rgba(0,0,0,0.9)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: metric.color,
                  fontSize: "16px",
                  fontWeight: "bold",
                }}
              >
                {metric.value.toFixed(0)}%
              </div>
            </div>
            <div style={{ color: "#ffffff", fontSize: "12px" }}>
              {metric.name}
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  const charts = [
    {
      name: "Flujo de Caja",
      component: <CSSCashFlowChart />,
    },
    {
      name: "Métricas Clave",
      component: <CSSRadialChart />,
    },
  ];

  return (
    <div
      ref={containerRef} // RESTAURAR: Referencia para el hover
      style={{
        background:
          "linear-gradient(135deg, rgba(0, 0, 20, 0.95), rgba(0, 20, 40, 0.9))",
        backdropFilter: "blur(20px)",
        border: "1px solid rgba(0, 255, 136, 0.3)",
        borderRadius: "20px",
        padding: "30px",
        margin: "20px 0",
        position: "relative",
        overflow: "hidden",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.5)",
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ position: "relative", zIndex: 1 }}
      >
        {/* RESTAURAR: Encabezado con efecto hover */}
        <AnimatePresence>
          {headerVisible && (
            <motion.h3
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              style={{
                color: "#00ff88",
                fontSize: "24px",
                fontWeight: "300",
                marginBottom: "30px",
                textAlign: "center",
                textShadow: "0 0 15px rgba(0, 255, 136, 0.6)",
                overflow: "hidden",
              }}
            >
              {title}
            </motion.h3>
          )}
        </AnimatePresence>

        {/* Métricas con efectos corregidos */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: "15px",
            marginBottom: "30px",
          }}
        >
          <motion.div
            whileHover={{
              scale: 1.05,
              backgroundColor: "rgba(0, 255, 136, 0.15)",
              boxShadow: "0 5px 15px rgba(0, 255, 136, 0.3)",
            }}
            transition={{ duration: 0.2 }}
            style={{
              background: "rgba(0, 255, 136, 0.1)",
              border: "1px solid rgba(0, 255, 136, 0.3)",
              borderRadius: "15px",
              padding: "15px",
              textAlign: "center",
              height: "90px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                color: "rgba(255, 255, 255, 0.7)",
                fontSize: "11px",
                marginBottom: "5px",
              }}
            >
              VPN
            </div>
            <animated.div
              style={{
                color: "#00ff88",
                fontSize: "16px",
                fontWeight: "bold",
                textShadow: "0 0 10px rgba(0, 255, 136, 0.5)",
              }}
            >
              {npvSpring.value.to(
                (val: number) => `$${Math.round(val).toLocaleString()}`
              )}
            </animated.div>
          </motion.div>

          <motion.div
            whileHover={{
              scale: 1.05,
              backgroundColor: "rgba(0, 136, 255, 0.15)",
              boxShadow: "0 5px 15px rgba(0, 136, 255, 0.3)",
            }}
            transition={{ duration: 0.2 }}
            style={{
              background: "rgba(0, 136, 255, 0.1)",
              border: "1px solid rgba(0, 136, 255, 0.3)",
              borderRadius: "15px",
              padding: "15px",
              textAlign: "center",
              height: "90px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                color: "rgba(255, 255, 255, 0.7)",
                fontSize: "11px",
                marginBottom: "5px",
              }}
            >
              TIR
            </div>
            <animated.div
              style={{
                color: "#0088ff",
                fontSize: "16px",
                fontWeight: "bold",
                textShadow: "0 0 10px rgba(0, 136, 255, 0.5)",
              }}
            >
              {irrSpring.value.to((val: number) => `${val.toFixed(1)}%`)}
            </animated.div>
          </motion.div>

          <motion.div
            whileHover={{
              scale: 1.05,
              backgroundColor: "rgba(136, 255, 0, 0.15)",
              boxShadow: "0 5px 15px rgba(136, 255, 0, 0.3)",
            }}
            transition={{ duration: 0.2 }}
            style={{
              background: "rgba(136, 255, 0, 0.1)",
              border: "1px solid rgba(136, 255, 0, 0.3)",
              borderRadius: "15px",
              padding: "15px",
              textAlign: "center",
              height: "90px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                color: "rgba(255, 255, 255, 0.7)",
                fontSize: "11px",
                marginBottom: "5px",
              }}
            >
              Sostenibilidad
            </div>
            <animated.div
              style={{
                color: "#88ff00",
                fontSize: "16px",
                fontWeight: "bold",
                textShadow: "0 0 10px rgba(136, 255, 0, 0.5)",
              }}
            >
              {sustainabilitySpring.value.to(
                (val: number) => `${val.toFixed(1)}/10`
              )}
            </animated.div>
          </motion.div>

          <motion.div
            whileHover={{
              scale: 1.05,
              backgroundColor: "rgba(255, 136, 0, 0.15)",
              boxShadow: "0 5px 15px rgba(255, 136, 0, 0.3)",
            }}
            transition={{ duration: 0.2 }}
            style={{
              background: "rgba(255, 136, 0, 0.1)",
              border: "1px solid rgba(255, 136, 0, 0.3)",
              borderRadius: "15px",
              padding: "15px",
              textAlign: "center",
              height: "90px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
          >
            <div
              style={{
                color: "rgba(255, 255, 255, 0.7)",
                fontSize: "11px",
                marginBottom: "5px",
              }}
            >
              Ubicación
            </div>
            <animated.div
              style={{
                color: "#ff8800",
                fontSize: "16px",
                fontWeight: "bold",
                textShadow: "0 0 10px rgba(255, 136, 0, 0.5)",
              }}
            >
              {locationSpring.value.to((val: number) => `${val.toFixed(1)}/10`)}
            </animated.div>
          </motion.div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "10px",
            marginBottom: "20px",
          }}
        >
          {charts.map((chart, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveChart(index)}
              style={{
                padding: "8px 16px",
                background:
                  activeChart === index
                    ? "linear-gradient(135deg, #00ff88, #00cc66)"
                    : "rgba(255, 255, 255, 0.1)",
                color: activeChart === index ? "#000" : "#fff",
                border: "1px solid rgba(0, 255, 136, 0.3)",
                borderRadius: "20px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "500",
                transition: "all 0.3s ease",
              }}
            >
              {chart.name}
            </motion.button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeChart}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.5 }}
            style={{
              background: "rgba(0, 0, 0, 0.3)",
              borderRadius: "15px",
              padding: "20px",
            }}
          >
            {charts[activeChart].component}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default AdvancedFuturisticCharts;
