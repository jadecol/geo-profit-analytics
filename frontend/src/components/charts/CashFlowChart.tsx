import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface CashFlowChartProps {
  cashFlows: number[];
  title?: string;
}

const CashFlowChart: React.FC<CashFlowChartProps> = ({ 
  cashFlows, 
  title = "Flujo de Caja Mensual" 
}) => {
  const displayFlows = cashFlows.slice(0, 12); // Solo primeros 12 meses
  
  const data = {
    labels: displayFlows.map((_, index) => `Mes ${index + 1}`),
    datasets: [
      {
        label: 'Flujo de Caja',
        data: displayFlows,
        backgroundColor: displayFlows.map(flow => 
          flow >= 0 ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)'
        ),
        borderColor: displayFlows.map(flow => 
          flow >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)'
        ),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const value = context.parsed.y;
            return `Flujo: $${value.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + Math.round(value).toLocaleString();
          }
        }
      },
    },
  };

  return (
    <div style={{ 
      marginTop: '30px', 
      padding: '20px', 
      backgroundColor: '#ffffff', 
      borderRadius: '8px',
      border: '1px solid #e0e0e0'
    }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default CashFlowChart;