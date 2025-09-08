// frontend/src/App.tsx
import React, { useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import ProjectForm from './components/Forms/ProjectForm';
import MapComponent from './components/Map/MapComponent';
import ResultsPanel from './components/Charts/ResultsPanel';
import { ProjectData } from './types';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

const App: React.FC = () => {
  const [projectData, setProjectData] = useState<ProjectData | null>(null);
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const handleProjectSubmit = (data: ProjectData) => {
    setProjectData(data);
    // Aquí se llamará a la API para análisis
    console.log('Datos del proyecto:', data);
  };

  return (
    <div className="App">
      <Container fluid>
        <Row>
          <Col md={4} className="sidebar">
            <h1 className="mt-3">GeoProfit Analytics</h1>
            <ProjectForm onSubmit={handleProjectSubmit} />
          </Col>
          <Col md={8}>
            <Row>
              <Col>
                <MapComponent />
              </Col>
            </Row>
            <Row>
              <Col>
                {analysisResults && <ResultsPanel results={analysisResults} />}
              </Col>
            </Row>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default App;
