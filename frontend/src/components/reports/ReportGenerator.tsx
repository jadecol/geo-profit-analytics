import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface ReportData {
  projectName: string;
  projectLocation: string;
  financial: {
    npv: number;
    irr: number;
    cashFlows: number[];
  };
  geospatial: {
    locationScore: number;
    accessibilityScore: number;
    riskFactors: string[];
    nearbyServices: string[];
  };
  sustainability: {
    overallScore: number;
    co2Reduction: number;
    waterSavings: number;
    energySavings: number;
  };
}

interface ReportGeneratorProps {
  reportData: ReportData;
  onBack: () => void;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ reportData, onBack }) => {
  const [reportType, setReportType] = useState<'executive' | 'detailed' | 'technical'>('executive');
  const [generating, setGenerating] = useState(false);
  const [exportFormat, setExportFormat] = useState<'pdf' | 'html' | 'docx'>('pdf');

  const generateReport = async () => {
    setGenerating(true);
    
    // Simular generación de reporte
    setTimeout(() => {
      if (exportFormat === 'html') {
        generateHTMLReport();
      } else {
        console.log(`Generando reporte ${reportType} en formato ${exportFormat}`);
      }
      setGenerating(false);
    }, 2000);
  };

  const generateHTMLReport = () => {
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Reporte de Análisis - ${reportData.projectName}</title>
        <style>
          body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
          }
          .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
          }
          .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid rgba(0, 255, 136, 0.3);
            padding-bottom: 20px;
          }
          .title {
            font-size: 32px;
            color: #00ff88;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
          }
          .subtitle {
            font-size: 18px;
            color: rgba(255, 255, 255, 0.7);
          }
          .section {
            margin: 30px 0;
            padding: 25px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
          }
          .section h2 {
            color: #00ff88;
            font-size: 24px;
            margin-bottom: 20px;
            text-shadow: 0 0 5px rgba(0, 255, 136, 0.3);
          }
          .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
          }
          .metric-card {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
          }
          .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
          }
          .metric-label {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 5px;
          }
          .conclusion {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 200, 100, 0.05));
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 15px;
            padding: 30px;
            margin-top: 40px;
            text-align: center;
          }
          .list-item {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 3px solid #00ff88;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1 class="title">REPORTE DE ANÁLISIS INTEGRAL</h1>
            <p class="subtitle">${reportData.projectName}</p>
            <p class="subtitle">Ubicación: ${reportData.projectLocation}</p>
            <p style="font-size: 14px; opacity: 0.7;">Generado: ${new Date().toLocaleDateString('es-CO')}</p>
          </div>

          <div class="section">
            <h2>🏆 Resumen Ejecutivo</h2>
            <p>El proyecto ${reportData.projectName} presenta las siguientes características principales:</p>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-value">$${Math.round(reportData.financial.npv).toLocaleString()}</div>
                <div class="metric-label">VPN</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">${(reportData.financial.irr * 100).toFixed(1)}%</div>
                <div class="metric-label">TIR</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">${reportData.geospatial.locationScore}/10</div>
                <div class="metric-label">Ubicación</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">${reportData.sustainability.overallScore}/10</div>
                <div class="metric-label">Sostenibilidad</div>
              </div>
            </div>
          </div>

          <div class="section">
            <h2>💰 Análisis Financiero</h2>
            <p><strong>Valor Presente Neto (VPN):</strong> $${Math.round(reportData.financial.npv).toLocaleString()}</p>
            <p><strong>Tasa Interna de Retorno (TIR):</strong> ${(reportData.financial.irr * 100).toFixed(2)}%</p>
            <p><strong>Evaluación:</strong> ${reportData.financial.npv > 0 ? 'Proyecto financieramente viable' : 'Requiere revisión financiera'}</p>
          </div>

          <div class="section">
            <h2>🗺️ Análisis Geoespacial</h2>
            <p><strong>Puntuación de Ubicación:</strong> ${reportData.geospatial.locationScore}/10</p>
            <p><strong>Accesibilidad:</strong> ${reportData.geospatial.accessibilityScore}/10</p>
            <h3>Servicios Cercanos:</h3>
            ${reportData.geospatial.nearbyServices.map(service => `<div class="list-item">• ${service}</div>`).join('')}
            <h3>Factores de Riesgo:</h3>
            ${reportData.geospatial.riskFactors.map(risk => `<div class="list-item">⚠️ ${risk}</div>`).join('')}
          </div>

          <div class="section">
            <h2>🌱 Análisis de Sostenibilidad</h2>
            <p><strong>Puntuación General:</strong> ${reportData.sustainability.overallScore}/10</p>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-value">+${reportData.sustainability.co2Reduction}%</div>
                <div class="metric-label">Reducción CO₂</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">+${reportData.sustainability.waterSavings}%</div>
                <div class="metric-label">Ahorro de Agua</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">+${reportData.sustainability.energySavings}%</div>
                <div class="metric-label">Eficiencia Energética</div>
              </div>
            </div>
          </div>

          <div class="conclusion">
            <h2>📋 Conclusiones y Recomendaciones</h2>
            <p><strong>Viabilidad del Proyecto:</strong> ${
              reportData.financial.npv > 0 && reportData.geospatial.locationScore > 6 && reportData.sustainability.overallScore > 6
                ? 'ALTAMENTE RECOMENDADO - El proyecto muestra indicadores positivos en todos los aspectos analizados.'
                : reportData.financial.npv > 0 || reportData.geospatial.locationScore > 6
                ? 'VIABLE CON CONSIDERACIONES - El proyecto presenta oportunidades pero requiere atención en algunas áreas.'
                : 'REQUIERE REVISIÓN - Se recomienda evaluar mejoras antes de proceder.'
            }</p>
          </div>
        </div>
      </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Reporte_${reportData.projectName.replace(/\s+/g, '_')}_${new Date().getTime()}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
      padding: '0'
    }}>
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
          color: 'white'
        }}
      >
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onBack} 
          style={{
            padding: '12px 24px',
            background: 'linear-gradient(135deg, #f43f5e, #e11d48)',
            color: 'white',
            border: 'none',
            borderRadius: '50px',
            cursor: 'pointer',
            marginRight: '20px',
            fontSize: '14px',
            fontWeight: '500',
            boxShadow: '0 4px 15px rgba(244, 63, 94, 0.4)'
          }}
        >
          Volver
        </motion.button>
        <h2 style={{ display: 'inline', fontSize: '24px', fontWeight: '300' }}>
          Generador de Reportes: {reportData.projectName}
        </h2>
      </motion.div>

      <div style={{ padding: '40px' }}>
        {/* Configuración del reporte */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '40px',
            marginBottom: '30px'
          }}
        >
          <h3 style={{ color: 'white', marginBottom: '30px', fontSize: '20px', fontWeight: '300' }}>
            Configuración del Reporte
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '30px' }}>
            {/* Tipo de reporte */}
            <div>
              <label style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px', marginBottom: '10px', display: 'block' }}>
                Tipo de Reporte
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {[
                  { key: 'executive', label: 'Ejecutivo', desc: 'Resumen para directivos' },
                  { key: 'detailed', label: 'Detallado', desc: 'Análisis completo' },
                  { key: 'technical', label: 'Técnico', desc: 'Información específica' }
                ].map((type) => (
                  <motion.label
                    key={type.key}
                    whileHover={{ scale: 1.02 }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '12px',
                      background: reportType === type.key ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                      border: `1px solid ${reportType === type.key ? 'rgba(0, 255, 136, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                      borderRadius: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <input
                      type="radio"
                      name="reportType"
                      value={type.key}
                      checked={reportType === type.key}
                      onChange={(e) => setReportType(e.target.value as any)}
                      style={{ marginRight: '10px' }}
                    />
                    <div>
                      <div style={{ color: 'white', fontWeight: '500' }}>{type.label}</div>
                      <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>{type.desc}</div>
                    </div>
                  </motion.label>
                ))}
              </div>
            </div>

            {/* Formato de exportación */}
            <div>
              <label style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px', marginBottom: '10px', display: 'block' }}>
                Formato de Exportación
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {[
                  { key: 'html', label: 'HTML', desc: 'Visualización web' },
                  { key: 'pdf', label: 'PDF', desc: 'Documento imprimible' },
                  { key: 'docx', label: 'DOCX', desc: 'Microsoft Word' }
                ].map((format) => (
                  <motion.label
                    key={format.key}
                    whileHover={{ scale: 1.02 }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '12px',
                      background: exportFormat === format.key ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                      border: `1px solid ${exportFormat === format.key ? 'rgba(59, 130, 246, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                      borderRadius: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <input
                      type="radio"
                      name="exportFormat"
                      value={format.key}
                      checked={exportFormat === format.key}
                      onChange={(e) => setExportFormat(e.target.value as any)}
                      style={{ marginRight: '10px' }}
                    />
                    <div>
                      <div style={{ color: 'white', fontWeight: '500' }}>{format.label}</div>
                      <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>{format.desc}</div>
                    </div>
                  </motion.label>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Botón de generación */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          style={{ textAlign: 'center' }}
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={generateReport}
            disabled={generating}
            style={{
              padding: '20px 40px',
              fontSize: '18px',
              background: generating 
                ? 'rgba(100, 100, 100, 0.5)' 
                : 'linear-gradient(135deg, #00ff88, #00cc66)',
              color: generating ? 'rgba(255, 255, 255, 0.5)' : 'black',
              border: 'none',
              borderRadius: '50px',
              cursor: generating ? 'not-allowed' : 'pointer',
              boxShadow: generating ? 'none' : '0 8px 25px rgba(0, 255, 136, 0.4)',
              fontWeight: '600',
              transition: 'all 0.3s ease'
            }}
          >
            {generating ? 'Generando Reporte...' : `Generar Reporte ${reportType.toUpperCase()}`}
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
};

export default ReportGenerator;