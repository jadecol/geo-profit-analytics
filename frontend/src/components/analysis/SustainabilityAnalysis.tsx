import React, { useState } from 'react';
import { analysisService } from '../../services/api';

interface SustainabilityAnalysisProps {
  projectId: number;
  projectName: string;
  onBack: () => void;
}

interface SustainabilityResult {
  overall_score: number;
  carbon_footprint: number;
  energy_efficiency: number;
  water_usage: number;
  waste_management: number;
  green_certifications: string[];
  recommendations: string[];
  environmental_impact: {
    co2_reduction: number;
    water_savings: number;
    energy_savings: number;
  };
}

const SustainabilityAnalysis: React.FC<SustainabilityAnalysisProps> = ({ 
  projectId, 
  projectName, 
  onBack 
}) => {
  const [result, setResult] = useState<SustainabilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await analysisService.runSustainabilityAnalysis(projectId);
      setResult(response.data);
    } catch (err: any) {
      // Datos simulados mientras se implementa el backend
      setTimeout(() => {
        setResult({
          overall_score: 8.2,
          carbon_footprint: 1250, // kg CO2 por m²
          energy_efficiency: 7.8,
          water_usage: 6.5,
          waste_management: 8.9,
          green_certifications: ['LEED Gold Candidate', 'BREEAM Very Good'],
          recommendations: [
            'Implementar paneles solares para reducir huella de carbono',
            'Sistema de recolección de agua lluvia',
            'Materiales de construcción sostenibles',
            'Certificación LEED Platinum alcanzable'
          ],
          environmental_impact: {
            co2_reduction: 35, // porcentaje
            water_savings: 42,
            energy_savings: 28
          }
        });
        setLoading(false);
      }, 2000);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return '#4CAF50';
    if (score >= 6) return '#FF9800';
    return '#f44336';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excelente';
    if (score >= 6) return 'Bueno';
    return 'Necesita Mejoras';
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      padding: '0'
    }}>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '20px 40px',
        color: 'white'
      }}>
        <button onClick={onBack} style={{
          padding: '10px 20px',
          backgroundColor: 'rgba(244, 67, 54, 0.8)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          marginRight: '20px',
          backdropFilter: 'blur(10px)'
        }}>
          Volver
        </button>
        <h2 style={{ display: 'inline', fontSize: '24px', fontWeight: '300' }}>
          Análisis de Sostenibilidad: {projectName}
        </h2>
      </div>

      <div style={{ padding: '40px' }}>
        {!result && (
          <div style={{
            textAlign: 'center',
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '20px',
            padding: '60px',
            maxWidth: '500px',
            margin: '100px auto'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🌱</div>
            <h3 style={{ color: 'white', marginBottom: '20px' }}>
              Análisis de Sostenibilidad Ambiental
            </h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '30px' }}>
              Evaluaremos el impacto ambiental y las oportunidades de sostenibilidad de tu proyecto
            </p>
            <button
              onClick={runAnalysis}
              disabled={loading}
              style={{
                padding: '15px 30px',
                fontSize: '18px',
                background: 'linear-gradient(135deg, #4CAF50, #45a049)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 6px 20px rgba(0, 0, 0, 0.2)'
              }}
            >
              {loading ? 'Analizando Sostenibilidad...' : 'Iniciar Análisis'}
            </button>
          </div>
        )}

        {result && (
          <>
            {/* Puntuación general */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '20px',
              padding: '40px',
              marginBottom: '30px',
              textAlign: 'center'
            }}>
              <h3 style={{ color: 'white', marginBottom: '20px' }}>Puntuación de Sostenibilidad</h3>
              <div style={{
                fontSize: '72px',
                fontWeight: 'bold',
                color: getScoreColor(result.overall_score),
                textShadow: '0 4px 8px rgba(0,0,0,0.3)',
                marginBottom: '10px'
              }}>
                {result.overall_score}/10
              </div>
              <div style={{
                fontSize: '24px',
                color: 'white',
                fontWeight: '300'
              }}>
                {getScoreLabel(result.overall_score)}
              </div>
            </div>

            {/* Métricas detalladas */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px',
              marginBottom: '30px'
            }}>
              {[
                { title: 'Eficiencia Energética', value: result.energy_efficiency, icon: '⚡' },
                { title: 'Uso del Agua', value: result.water_usage, icon: '💧' },
                { title: 'Gestión de Residuos', value: result.waste_management, icon: '♻️' },
                { title: 'Huella de Carbono', value: result.carbon_footprint, icon: '🌍', unit: 'kg CO₂/m²' }
              ].map((metric, index) => (
                <div key={index} style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(15px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '15px',
                  padding: '25px',
                  textAlign: 'center',
                  color: 'white'
                }}>
                  <div style={{ fontSize: '32px', marginBottom: '10px' }}>{metric.icon}</div>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.8 }}>
                    {metric.title}
                  </h4>
                  <div style={{
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: metric.unit ? 'white' : getScoreColor(metric.value)
                  }}>
                    {metric.value}{metric.unit || '/10'}
                  </div>
                </div>
              ))}
            </div>

            {/* Impacto ambiental */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '20px',
              padding: '30px',
              marginBottom: '30px'
            }}>
              <h3 style={{ color: 'white', marginBottom: '25px' }}>Impacto Ambiental Proyectado</h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '20px'
              }}>
                {[
                  { label: 'Reducción CO₂', value: result.environmental_impact.co2_reduction, color: '#4CAF50' },
                  { label: 'Ahorro de Agua', value: result.environmental_impact.water_savings, color: '#2196F3' },
                  { label: 'Ahorro Energético', value: result.environmental_impact.energy_savings, color: '#FF9800' }
                ].map((impact, index) => (
                  <div key={index} style={{
                    background: `linear-gradient(135deg, ${impact.color}20, ${impact.color}40)`,
                    border: `1px solid ${impact.color}60`,
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: impact.color }}>
                      +{impact.value}%
                    </div>
                    <div style={{ color: 'white', fontSize: '14px', marginTop: '5px' }}>
                      {impact.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Certificaciones y recomendaciones */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '30px'
            }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(15px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '20px',
                padding: '30px'
              }}>
                <h3 style={{ color: 'white', marginBottom: '20px' }}>Certificaciones Posibles</h3>
                {result.green_certifications.map((cert, index) => (
                  <div key={index} style={{
                    background: 'rgba(76, 175, 80, 0.2)',
                    border: '1px solid rgba(76, 175, 80, 0.4)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    margin: '10px 0',
                    color: 'white'
                  }}>
                    ✓ {cert}
                  </div>
                ))}
              </div>

              <div style={{
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(15px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '20px',
                padding: '30px'
              }}>
                <h3 style={{ color: 'white', marginBottom: '20px' }}>Recomendaciones</h3>
                {result.recommendations.map((rec, index) => (
                  <div key={index} style={{
                    background: 'rgba(33, 150, 243, 0.2)',
                    border: '1px solid rgba(33, 150, 243, 0.4)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    margin: '10px 0',
                    color: 'white',
                    fontSize: '14px'
                  }}>
                    💡 {rec}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SustainabilityAnalysis;