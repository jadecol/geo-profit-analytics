import CashFlowChart from '../charts/CashFlowChart';
import React, { useState } from 'react';
import { analysisService } from '../../services/api';

interface ProjectAnalysisProps {
  projectId: number;
  projectName: string;
  onBack: () => void;
}

interface AnalysisResult {
  npv: number;
  irr: number; 
  basic_metrics?: any;
  roi_percentage?: number;
  cash_flows?: number[];
  months?: string[];
  monthly_cash_flows?: number[];
  analysis_summary?: {
    construction_phase_months: number;
    selling_phase_months: number;
    total_months: number;
  };
}

const ProjectAnalysis: React.FC<ProjectAnalysisProps> = ({ projectId, projectName, onBack }) => {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await analysisService.runFinancialAnalysis(projectId);
      console.log('Datos recibidos del backend:', response.data);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error ejecutando análisis');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || isNaN(value)) {
      return 'N/A';
    }
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: any) => {
    console.log('Formatting percentage:', value, typeof value);
    
    if (value === undefined || value === null) {
      return 'N/A';
    }
    
    if (typeof value === 'string') {
      if (value.includes('YayA') || value === 'YayA%') {
        return 'N/A';
      }
      return value;
    }
    
    if (typeof value === 'number' && !isNaN(value) && isFinite(value)) {
      return `${(value * 100).toFixed(2)}%`;
    }
    
    return 'N/A';
  };

  const calculateTotals = (result: AnalysisResult) => {
    if (result.cash_flows && result.cash_flows.length > 0) {
      const totalInvestment = result.cash_flows
        .filter(flow => flow < 0)
        .reduce((sum, flow) => sum + Math.abs(flow), 0);
      
      const totalRevenue = result.cash_flows
        .filter(flow => flow > 0)
        .reduce((sum, flow) => sum + flow, 0);
      
      return {
        total_investment: totalInvestment,
        total_revenue: totalRevenue,
        cash_flows: result.cash_flows
      };
    }
    return {
      total_investment: 0,
      total_revenue: 0,
      cash_flows: result.cash_flows
    };
  };

  const isValidIRR = (irr: any): boolean => {
    return typeof irr === 'number' && !isNaN(irr) && isFinite(irr);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={onBack} style={{
          padding: '10px 20px',
          backgroundColor: '#f44336',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginRight: '20px'
        }}>
          Volver
        </button>
        <h2 style={{ display: 'inline' }}>Análisis Financiero: {projectName}</h2>
      </div>

      {!result && (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <button
            onClick={runAnalysis}
            disabled={loading}
            style={{
              padding: '15px 30px',
              fontSize: '18px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Analizando...' : 'Ejecutar Análisis Financiero'}
          </button>
        </div>
      )}

      {error && (
        <div style={{
          color: 'red',
          backgroundColor: '#ffebee',
          padding: '15px',
          borderRadius: '5px',
          marginTop: '20px'
        }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '30px' }}>
          {(() => {
            const calculatedTotals = calculateTotals(result);
            return (
              <>
                {/* Indicadores principales */}
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '20px',
                  marginBottom: '30px'
                }}>
                  <div style={{
                    backgroundColor: result.npv > 0 ? '#e8f5e8' : '#ffebee',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <h3>VPN (Valor Presente Neto)</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>
                      {formatCurrency(result.npv)}
                    </p>
                    <p style={{ fontSize: '12px', color: '#666' }}>
                      {result.npv > 0 ? 'Proyecto rentable' : 'Proyecto no rentable'}
                    </p>
                  </div>

                  <div style={{
                    backgroundColor: (isValidIRR(result.irr) && result.irr > 0.12) ? '#e8f5e8' : '#fff3e0',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <h3>TIR (Tasa Interna de Retorno)</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>
                      {formatPercentage(result.irr)}
                    </p>
                    <p style={{ fontSize: '12px', color: '#666' }}>
                      Tasa de descuento: 12%
                    </p>
                  </div>

                  <div style={{
                    backgroundColor: '#f3e5f5',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <h3>Inversión Total</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>
                      {formatCurrency(calculatedTotals.total_investment)}
                    </p>
                  </div>

                  <div style={{
                    backgroundColor: '#e3f2fd',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <h3>Ingresos Totales</h3>
                    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '10px 0' }}>
                      {formatCurrency(calculatedTotals.total_revenue)}
                    </p>
                  </div>
                </div>

                {/* Resumen de análisis */}
                <div style={{
                  backgroundColor: '#f9f9f9',
                  padding: '20px',
                  borderRadius: '8px',
                  marginTop: '20px'
                }}>
                  <h3>Resumen de Análisis</h3>
                  <div style={{ marginTop: '15px' }}>
                    <p><strong>Inversión Total:</strong> {formatCurrency(calculatedTotals.total_investment)}</p>
                    <p><strong>Ingresos Estimados:</strong> {formatCurrency(calculatedTotals.total_revenue)}</p>
                    <p><strong>Rentabilidad:</strong> {result.npv > 0 ? 'Proyecto Rentable' : 'Proyecto No Rentable'}</p>
                    <p><strong>TIR vs Descuento:</strong> {
                      (isValidIRR(result.irr) && result.irr > 0.12) 
                        ? `Supera tasa de descuento (${formatPercentage(result.irr)} > 12%)` 
                        : 'Por debajo de tasa de descuento'
                    }</p>
                    {result.roi_percentage && (
                      <p><strong>ROI:</strong> {formatPercentage(result.roi_percentage / 100)}</p>
                    )}
                  </div>

                  {/* Flujo de caja */}
                  {calculatedTotals.cash_flows && calculatedTotals.cash_flows.length > 0 && (
                    <div style={{ marginTop: '20px' }}>
                      <h4>Flujo de Caja por Periodo (Primeros 12 meses)</h4>
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '15px' }}>
                          <thead>
                            <tr style={{ backgroundColor: '#e0e0e0' }}>
                              <th style={{ padding: '10px', border: '1px solid #ccc' }}>Periodo</th>
                              <th style={{ padding: '10px', border: '1px solid #ccc' }}>Flujo de Caja</th>
                              <th style={{ padding: '10px', border: '1px solid #ccc' }}>Acumulado</th>
                            </tr>
                          </thead>
                          <tbody>
                            {calculatedTotals.cash_flows.slice(0, 12).map((flow, index) => {
                              const accumulated = calculatedTotals.cash_flows!.slice(0, index + 1).reduce((sum, f) => sum + f, 0);
                              return (
                                <tr key={index}>
                                  <td style={{ padding: '10px', border: '1px solid #ccc', textAlign: 'center' }}>
                                    {`Mes ${index + 1}`}
                                  </td>
                                  <td style={{ 
                                    padding: '10px', 
                                    border: '1px solid #ccc', 
                                    textAlign: 'right',
                                    color: flow >= 0 ? 'green' : 'red'
                                  }}>
                                    {formatCurrency(flow)}
                                  </td>
                                  <td style={{ 
                                    padding: '10px', 
                                    border: '1px solid #ccc', 
                                    textAlign: 'right',
                                    fontWeight: accumulated >= 0 ? 'bold' : 'normal',
                                    color: accumulated >= 0 ? 'green' : 'red'
                                  }}>
                                    {formatCurrency(accumulated)}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                      <CashFlowChart 
                        cashFlows={calculatedTotals.cash_flows} 
                        title="Análisis Visual del Flujo de Caja"
                      />
                    </div>
                  )}
                </div>

                <div style={{ marginTop: '30px', textAlign: 'center' }}>
                  <button
                    onClick={runAnalysis}
                    style={{
                      padding: '12px 24px',
                      backgroundColor: '#2196F3',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer'
                    }}
                  >
                    Recalcular Análisis
                  </button>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default ProjectAnalysis;