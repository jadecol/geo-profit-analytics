import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { analysisService } from "../../services/api";
import CashFlowChart from "../charts/CashFlowChart";
import AdvancedFuturisticCharts from "../charts/AdvancedFuturisticCharts";

interface IntegratedAnalysisProps {
  projectId: number;
  projectName: string;
  projectLocation: string;
  onBack: () => void;
  onNavigate: (section: "reports", params: { reportData: any }) => void;
}

interface AnalysisData {
  financial: any;
  geospatial: any;
  sustainability: any;
  loading: {
    financial: boolean;
    geospatial: boolean;
    sustainability: boolean;
  };
}

const IntegratedAnalysisDashboard: React.FC<IntegratedAnalysisProps> = ({
  projectId,
  projectName,
  projectLocation,
  onBack,
  onNavigate,
}) => {
  const [analysisData, setAnalysisData] = useState<AnalysisData>({
    financial: null,
    geospatial: null,
    sustainability: null,
    loading: {
      financial: false,
      geospatial: false,
      sustainability: false,
    },
  });

  const [activeSection, setActiveSection] = useState<
    "overview" | "financial" | "geospatial" | "sustainability"
  >("overview");

  // RESTAURAR: Estado para el efecto hover del header completo
  const [headerVisible, setHeaderVisible] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    runAllAnalyses();
  }, [projectId]);

  // RESTAURAR: Efecto hover del header completo
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

  const runAllAnalyses = async () => {
    setAnalysisData((prev) => ({
      ...prev,
      loading: { ...prev.loading, financial: true },
    }));

    try {
      const financialResponse = await analysisService.runFinancialAnalysis(
        projectId
      );
      setAnalysisData((prev) => ({
        ...prev,
        financial: financialResponse.data,
        loading: { ...prev.loading, financial: false },
      }));
    } catch (error) {
      setAnalysisData((prev) => ({
        ...prev,
        loading: { ...prev.loading, financial: false },
      }));
    }

    setAnalysisData((prev) => ({
      ...prev,
      loading: { ...prev.loading, geospatial: true },
    }));

    setTimeout(() => {
      setAnalysisData((prev) => ({
        ...prev,
        geospatial: {
          location_score: 7.5,
          accessibility_score: 8.2,
          risk_factors: ["Zona de inundación baja", "Tráfico moderado"],
          nearby_services: ["Hospital a 2km", "Centro comercial a 1.5km"],
        },
        loading: { ...prev.loading, geospatial: false },
      }));
    }, 1500);

    setAnalysisData((prev) => ({
      ...prev,
      loading: { ...prev.loading, sustainability: true },
    }));

    setTimeout(() => {
      setAnalysisData((prev) => ({
        ...prev,
        sustainability: {
          overall_score: 8.2,
          carbon_footprint: 1250,
          energy_efficiency: 7.8,
          environmental_impact: {
            co2_reduction: 35,
            water_savings: 42,
            energy_savings: 28,
          },
        },
        loading: { ...prev.loading, sustainability: false },
      }));
    }, 2000);
  };

  const getOverallProjectScore = () => {
    const { financial, geospatial, sustainability } = analysisData;
    const scores: number[] = [];

    if (financial && !analysisData.loading.financial) {
      const financialScore = financial.npv > 0 ? 8.5 : 4.0;
      scores.push(financialScore);
    }

    if (geospatial && !analysisData.loading.geospatial) {
      const geoScore =
        (geospatial.location_score + geospatial.accessibility_score) / 2;
      scores.push(geoScore);
    }

    if (sustainability && !analysisData.loading.sustainability) {
      scores.push(sustainability.overall_score);
    }

    return scores.length > 0
      ? scores.reduce((sum, score) => sum + score, 0) / scores.length
      : 0;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const overallScore = getOverallProjectScore();

  const handleGenerateReport = () => {
  console.log("Botón presionado"); // Agrega esto para debug
  console.log("analysisData:", analysisData); // Verifica los datos
  
  const reportData = {
    projectName,
    projectLocation,
    financial: {
      npv: analysisData.financial?.npv || 0,
      irr: analysisData.financial?.irr || 0,
      cashFlows: analysisData.financial?.cash_flows || [],
    },
    geospatial: {
      locationScore: analysisData.geospatial?.location_score || 0,
      accessibilityScore: analysisData.geospatial?.accessibility_score || 0,
      riskFactors: analysisData.geospatial?.risk_factors || [],
      nearbyServices: analysisData.geospatial?.nearby_services || [],
    },
    sustainability: {
      overallScore: analysisData.sustainability?.overall_score || 0,
      co2Reduction: analysisData.sustainability?.environmental_impact?.co2_reduction || 0,
      waterSavings: analysisData.sustainability?.environmental_impact?.water_savings || 0,
      energySavings: analysisData.sustainability?.environmental_impact?.energy_savings || 0,
    },
  };
  
  console.log("reportData:", reportData); // Verifica los datos del reporte
  console.log("onNavigate:", onNavigate); // Verifica que la función existe
  
  onNavigate("reports", { reportData });
};

  return (
    <div
      ref={containerRef}
      className="dashboard-container"
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, #0a0a1a 0%, #121228 50%, #0a1432 100%)",
        padding: "0",
        position: "relative",
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
          radial-gradient(circle at 10% 20%, rgba(0, 255, 136, 0.05) 0%, transparent 25%),
          radial-gradient(circle at 90% 80%, rgba(0, 136, 255, 0.05) 0%, transparent 25%),
          radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.03) 0%, transparent 50%)
        `,
          zIndex: 0,
        }}
      />

      {/* Grid de fondo */}
      <svg
        width="100%"
        height="100%"
        style={{ position: "absolute", top: 0, left: 0, zIndex: 0 }}
      >
        <line
          x1="0"
          y1="33%"
          x2="100%"
          y2="33%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
        <line
          x1="0"
          y1="66%"
          x2="100%"
          y2="66%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
        <line
          x1="20%"
          y1="0"
          x2="20%"
          y2="100%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
        <line
          x1="40%"
          y1="0"
          x2="40%"
          y2="100%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
        <line
          x1="60%"
          y1="0"
          x2="60%"
          y2="100%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
        <line
          x1="80%"
          y1="0"
          x2="80%"
          y2="100%"
          stroke="rgba(255, 255, 255, 0.03)"
          strokeWidth="1"
        />
      </svg>

      {/* RESTAURAR: Header con efecto hover completo */}
      <AnimatePresence>
        {headerVisible && (
          <motion.div
            initial={{ opacity: 0, y: -20, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -20, height: 0 }}
            transition={{ duration: 0.4 }}
            style={{
              background: "rgba(10, 15, 30, 0.7)",
              backdropFilter: "blur(20px)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
              padding: "20px 40px",
              position: "sticky",
              top: 0,
              zIndex: 100,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "20px",
              }}
            >
              <div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={onBack}
                  style={{
                    padding: "12px 24px",
                    background: "linear-gradient(135deg, #ff6b6b, #ee5a52)",
                    color: "white",
                    border: "none",
                    borderRadius: "50px",
                    cursor: "pointer",
                    marginRight: "20px",
                    fontSize: "14px",
                    fontWeight: "500",
                    boxShadow: "0 4px 15px rgba(255, 107, 107, 0.4)",
                    transition: "all 0.3s ease",
                  }}
                >
                  Dashboard
                </motion.button>

                <motion.span
                  style={{
                    color: "white",
                    fontSize: "24px",
                    fontWeight: "300",
                  }}
                >
                  Análisis Integral: {projectName}
                </motion.span>
              </div>

              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
                style={{
                  background:
                    "linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(255, 255, 255, 0.2)",
                  borderRadius: "20px",
                  padding: "15px 25px",
                  textAlign: "center",
                }}
              >
                <div style={{ color: "white", fontSize: "12px", opacity: 0.8 }}>
                  Puntuación General
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  style={{
                    color:
                      overallScore >= 8
                        ? "#4ade80"
                        : overallScore >= 6
                        ? "#fbbf24"
                        : overallScore > 0
                        ? "#f87171"
                        : "#9ca3af",
                    fontSize: "28px",
                    fontWeight: "bold",
                    textShadow: "0 0 10px currentColor",
                  }}
                >
                  {overallScore > 0 ? overallScore.toFixed(1) : "0.0"}/10
                </motion.div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              style={{ display: "flex", gap: "10px" }}
            >
              {[
                { key: "overview", label: "Resumen", icon: "📊" },
                { key: "financial", label: "Financiero", icon: "💰" },
                { key: "geospatial", label: "Ubicación", icon: "🗺️" },
                { key: "sustainability", label: "Sostenibilidad", icon: "🌱" },
              ].map((tab, index) => (
                <motion.button
                  key={tab.key}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setActiveSection(tab.key as any)}
                  style={{
                    padding: "12px 20px",
                    background:
                      activeSection === tab.key
                        ? "linear-gradient(135deg, #3b82f6, #1d4ed8)"
                        : "rgba(255, 255, 255, 0.1)",
                    color: "white",
                    border:
                      activeSection === tab.key
                        ? "2px solid #60a5fa"
                        : "1px solid rgba(255, 255, 255, 0.2)",
                    borderRadius: "12px",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "500",
                    transition: "all 0.3s ease",
                    boxShadow:
                      activeSection === tab.key
                        ? "0 0 20px rgba(59, 130, 246, 0.5)"
                        : "none",
                  }}
                >
                  {tab.icon} {tab.label}
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div style={{ padding: "40px" }}>
        <AnimatePresence mode="wait">
          {activeSection === "overview" && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <AdvancedFuturisticCharts
                cashFlows={analysisData.financial?.cash_flows}
                npv={analysisData.financial?.npv || 0}
                irr={analysisData.financial?.irr || 0}
                sustainability={analysisData.sustainability?.overall_score || 0}
                location={analysisData.geospatial?.location_score || 0}
                title="Dashboard de Análisis Integral"
              />

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
                  gap: "30px",
                  marginTop: "40px",
                }}
              >
                {/* Tarjeta Financiera */}
                <motion.div
                  whileHover={{
                    scale: 1.02,
                    y: -5,
                    boxShadow: "0 10px 30px rgba(34, 197, 94, 0.3)",
                  }}
                  transition={{ type: "spring", stiffness: 200 }}
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.05))",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(34, 197, 94, 0.3)",
                    borderRadius: "20px",
                    padding: "30px",
                    position: "relative",
                    overflow: "hidden",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                  }}
                  onClick={() => setActiveSection("financial")}
                >
                  <motion.div
                    animate={{
                      scale: [1, 1.1, 1],
                      rotate: [0, 180, 360],
                    }}
                    transition={{
                      duration: 8,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                    style={{
                      position: "absolute",
                      top: "-50%",
                      right: "-50%",
                      width: "200px",
                      height: "200px",
                      background:
                        "radial-gradient(circle, rgba(34, 197, 94, 0.1) 0%, transparent 70%)",
                      borderRadius: "50%",
                    }}
                  />

                  <h3
                    style={{
                      color: "white",
                      marginBottom: "20px",
                      fontSize: "18px",
                      fontWeight: "500",
                    }}
                  >
                    💰 Análisis Financiero
                  </h3>

                  {analysisData.loading.financial ? (
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{
                        color: "rgba(255, 255, 255, 0.7)",
                        textAlign: "center",
                        padding: "20px",
                      }}
                    >
                      Analizando viabilidad financiera...
                    </motion.div>
                  ) : analysisData.financial ? (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "1fr 1fr",
                          gap: "15px",
                          marginBottom: "20px",
                        }}
                      >
                        <motion.div
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: "rgba(34, 197, 94, 0.1)",
                          }}
                          transition={{ duration: 0.2 }}
                          style={{
                            padding: "10px",
                            borderRadius: "8px",
                            cursor: "pointer",
                          }}
                        >
                          <div
                            style={{
                              color: "rgba(255, 255, 255, 0.7)",
                              fontSize: "12px",
                            }}
                          >
                            VPN
                          </div>
                          <div
                            style={{
                              color: "#22c55e",
                              fontSize: "20px",
                              fontWeight: "bold",
                            }}
                          >
                            {formatCurrency(analysisData.financial.npv)}
                          </div>
                        </motion.div>

                        <motion.div
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: "rgba(34, 197, 94, 0.1)",
                          }}
                          transition={{ duration: 0.2 }}
                          style={{
                            padding: "10px",
                            borderRadius: "8px",
                            cursor: "pointer",
                          }}
                        >
                          <div
                            style={{
                              color: "rgba(255, 255, 255, 0.7)",
                              fontSize: "12px",
                            }}
                          >
                            TIR
                          </div>
                          <div
                            style={{
                              color: "#22c55e",
                              fontSize: "20px",
                              fontWeight: "bold",
                            }}
                          >
                            {(analysisData.financial.irr * 100).toFixed(1)}%
                          </div>
                        </motion.div>
                      </div>

                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        style={{
                          background: "rgba(34, 197, 94, 0.2)",
                          borderRadius: "10px",
                          padding: "10px",
                          textAlign: "center",
                          color: "white",
                          fontSize: "14px",
                        }}
                      >
                        {analysisData.financial.npv > 0
                          ? "Proyecto Rentable ✓"
                          : "Revisar Viabilidad ⚠️"}
                      </motion.div>
                    </motion.div>
                  ) : (
                    <div style={{ color: "rgba(255, 255, 255, 0.5)" }}>
                      Sin datos
                    </div>
                  )}
                </motion.div>

                {/* Tarjeta Geoespacial */}
                <motion.div
                  whileHover={{
                    scale: 1.02,
                    y: -5,
                    boxShadow: "0 10px 30px rgba(249, 115, 22, 0.3)",
                  }}
                  transition={{ type: "spring", stiffness: 200 }}
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(234, 88, 12, 0.05))",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(249, 115, 22, 0.3)",
                    borderRadius: "20px",
                    padding: "30px",
                    position: "relative",
                    overflow: "hidden",
                    cursor: "pointer",
                  }}
                  onClick={() => setActiveSection("geospatial")}
                >
                  <motion.div
                    animate={{
                      scale: [1, 1.2, 1],
                      x: [-10, 10, -10],
                    }}
                    transition={{
                      duration: 6,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                    style={{
                      position: "absolute",
                      bottom: "-50%",
                      left: "-50%",
                      width: "200px",
                      height: "200px",
                      background:
                        "radial-gradient(circle, rgba(249, 115, 22, 0.1) 0%, transparent 70%)",
                      borderRadius: "50%",
                    }}
                  />

                  <h3
                    style={{
                      color: "white",
                      marginBottom: "20px",
                      fontSize: "18px",
                      fontWeight: "500",
                    }}
                  >
                    🗺️ Análisis Geoespacial
                  </h3>

                  {analysisData.loading.geospatial ? (
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{
                        color: "rgba(255, 255, 255, 0.7)",
                        textAlign: "center",
                        padding: "20px",
                      }}
                    >
                      Evaluando ubicación...
                    </motion.div>
                  ) : analysisData.geospatial ? (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 }}
                    >
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "1fr 1fr",
                          gap: "15px",
                          marginBottom: "20px",
                        }}
                      >
                        <motion.div
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: "rgba(249, 115, 22, 0.1)",
                          }}
                          style={{
                            padding: "10px",
                            borderRadius: "8px",
                          }}
                        >
                          <div
                            style={{
                              color: "rgba(255, 255, 255, 0.7)",
                              fontSize: "12px",
                            }}
                          >
                            Ubicación
                          </div>
                          <div
                            style={{
                              color: "#f97316",
                              fontSize: "20px",
                              fontWeight: "bold",
                            }}
                          >
                            {analysisData.geospatial.location_score}/10
                          </div>
                        </motion.div>

                        <motion.div
                          whileHover={{
                            scale: 1.05,
                            backgroundColor: "rgba(249, 115, 22, 0.1)",
                          }}
                          style={{
                            padding: "10px",
                            borderRadius: "8px",
                          }}
                        >
                          <div
                            style={{
                              color: "rgba(255, 255, 255, 0.7)",
                              fontSize: "12px",
                            }}
                          >
                            Accesibilidad
                          </div>
                          <div
                            style={{
                              color: "#f97316",
                              fontSize: "20px",
                              fontWeight: "bold",
                            }}
                          >
                            {analysisData.geospatial.accessibility_score}/10
                          </div>
                        </motion.div>
                      </div>

                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        style={{
                          background: "rgba(249, 115, 22, 0.2)",
                          borderRadius: "10px",
                          padding: "10px",
                          textAlign: "center",
                          color: "white",
                          fontSize: "14px",
                        }}
                      >
                        Ubicación Favorable ✓
                      </motion.div>
                    </motion.div>
                  ) : (
                    <div style={{ color: "rgba(255, 255, 255, 0.5)" }}>
                      Sin datos
                    </div>
                  )}
                </motion.div>

                {/* Tarjeta Sostenibilidad */}
                <motion.div
                  whileHover={{
                    scale: 1.02,
                    y: -5,
                    boxShadow: "0 10px 30px rgba(16, 185, 129, 0.3)",
                  }}
                  transition={{ type: "spring", stiffness: 200 }}
                  style={{
                    background:
                      "linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.05))",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                    borderRadius: "20px",
                    padding: "30px",
                    position: "relative",
                    overflow: "hidden",
                    cursor: "pointer",
                  }}
                  onClick={() => setActiveSection("sustainability")}
                >
                  <motion.div
                    animate={{
                      rotate: [0, 360],
                      scale: [1, 1.1, 1],
                    }}
                    transition={{
                      duration: 10,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                    style={{
                      position: "absolute",
                      top: "-25%",
                      right: "-25%",
                      width: "150px",
                      height: "150px",
                      background:
                        "radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%)",
                      borderRadius: "50%",
                    }}
                  />

                  <h3
                    style={{
                      color: "white",
                      marginBottom: "20px",
                      fontSize: "18px",
                      fontWeight: "500",
                    }}
                  >
                    🌱 Sostenibilidad
                  </h3>

                  {analysisData.loading.sustainability ? (
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{
                        color: "rgba(255, 255, 255, 0.7)",
                        textAlign: "center",
                        padding: "20px",
                      }}
                    >
                      Evaluando impacto ambiental...
                    </motion.div>
                  ) : analysisData.sustainability ? (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 }}
                    >
                      <div
                        style={{ textAlign: "center", marginBottom: "20px" }}
                      >
                        <div
                          style={{
                            color: "rgba(255, 255, 255, 0.7)",
                            fontSize: "12px",
                          }}
                        >
                          Puntuación General
                        </div>
                        <motion.div
                          whileHover={{
                            scale: 1.1,
                            textShadow: "0 0 15px #10b981",
                          }}
                          style={{
                            color: "#10b981",
                            fontSize: "32px",
                            fontWeight: "bold",
                            cursor: "pointer",
                          }}
                        >
                          {analysisData.sustainability.overall_score}/10
                        </motion.div>
                      </div>

                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        style={{
                          background: "rgba(16, 185, 129, 0.2)",
                          borderRadius: "10px",
                          padding: "10px",
                          textAlign: "center",
                          color: "white",
                          fontSize: "14px",
                        }}
                      >
                        Proyecto Sostenible ✓
                      </motion.div>
                    </motion.div>
                  ) : (
                    <div style={{ color: "rgba(255, 255, 255, 0.5)" }}>
                      Sin datos
                    </div>
                  )}
                </motion.div>
              </motion.div>

              {/* Botón Generar Reporte */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                style={{ textAlign: "center", marginTop: "40px" }}
              >
                <motion.button
                  whileHover={{ 
                    scale: 1.05,
                    boxShadow: "0 8px 25px rgba(139, 92, 246, 0.6)"
                  }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleGenerateReport}
                  style={{
                    padding: "15px 30px",
                    background: "linear-gradient(135deg, #8b5cf6, #7c3aed)",
                    color: "white",
                    border: "none",
                    borderRadius: "50px",
                    cursor: "pointer",
                    fontSize: "16px",
                    fontWeight: "500",
                    boxShadow: "0 6px 20px rgba(139, 92, 246, 0.4)",
                    transition: "all 0.3s ease"
                  }}
                >
                  📄 Generar Reporte Ejecutivo
                </motion.button>
              </motion.div>
            </motion.div>
          )}

          {/* Secciones detalladas */}
          {activeSection === "financial" && analysisData.financial && (
            <motion.div
              key="financial"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.5 }}
            >
              <h2
                style={{
                  color: "white",
                  marginBottom: "30px",
                  fontSize: "28px",
                  fontWeight: "300",
                }}
              >
                Análisis Financiero Detallado
              </h2>
              {analysisData.financial.cash_flows && (
                <CashFlowChart
                  cashFlows={analysisData.financial.cash_flows}
                  title="Flujo de Caja Proyectado"
                />
              )}
            </motion.div>
          )}

          {activeSection === "geospatial" && analysisData.geospatial && (
            <motion.div
              key="geospatial"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.5 }}
            >
              <h2
                style={{
                  color: "white",
                  marginBottom: "30px",
                  fontSize: "28px",
                  fontWeight: "300",
                }}
              >
                Análisis Geoespacial Detallado
              </h2>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                style={{
                  background: "rgba(255, 255, 255, 0.05)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "20px",
                  padding: "40px",
                  color: "white",
                }}
              >
                <p>Ubicación: {projectLocation}</p>
                <p>
                  Puntuación de ubicación:{" "}
                  {analysisData.geospatial.location_score}/10
                </p>
                <p>
                  Servicios cercanos:{" "}
                  {analysisData.geospatial.nearby_services?.join(", ")}
                </p>
              </motion.div>
            </motion.div>
          )}

          {activeSection === "sustainability" &&
            analysisData.sustainability && (
              <motion.div
                key="sustainability"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.5 }}
              >
                <h2
                  style={{
                    color: "white",
                    marginBottom: "30px",
                    fontSize: "28px",
                    fontWeight: "300",
                  }}
                >
                  Análisis de Sostenibilidad Detallado
                </h2>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  style={{
                    background: "rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "20px",
                    padding: "40px",
                    color: "white",
                  }}
                >
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(200px, 1fr))",
                      gap: "20px",
                    }}
                  >
                    {[
                      {
                        label: "Reducción CO₂",
                        value:
                          analysisData.sustainability.environmental_impact
                            .co2_reduction,
                        color: "#10b981",
                        unit: "%",
                      },
                      {
                        label: "Ahorro de Agua",
                        value:
                          analysisData.sustainability.environmental_impact
                            .water_savings,
                        color: "#3b82f6",
                        unit: "%",
                      },
                      {
                        label: "Eficiencia Energética",
                        value:
                          analysisData.sustainability.environmental_impact
                            .energy_savings,
                        color: "#f59e0b",
                        unit: "%",
                      },
                    ].map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 * index }}
                        whileHover={{ scale: 1.05 }}
                      >
                        <h4>{item.label}</h4>
                        <div style={{ fontSize: "24px", color: item.color }}>
                          +{item.value}
                          {item.unit}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default IntegratedAnalysisDashboard;
