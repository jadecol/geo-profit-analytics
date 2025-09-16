// frontend/src/App.tsx
import React, { useState } from "react";
import "./App.css";
import Dashboard from "./components/dashboard/Dashboard";
import ProjectList from "./components/projects/ProjectList";
import ProjectForm from "./components/projects/ProjectForm";
import ProjectAnalysis from "./components/projects/ProjectAnalysis";
import GeospatialAnalysis from "./components/analysis/GeospatialAnalysis";
import SustainabilityAnalysis from "./components/analysis/SustainabilityAnalysis";
import IntegratedAnalysisDashboard from "./components/analysis/IntegratedAnalysisDashboard";
import ReportGenerator from "./components/reports/ReportGenerator";
import ProjectComparison from './components/comparison/ProjectComparison';

type Page =
  | "dashboard"
  | "projects"
  | "newProject"
  | "analysis"
  | "geospatial"
  | "sustainability"
  | "integrated"
  | "reports"
  | "advanced"
  | "comparison";

interface NavigationData {
  projectId?: number;
  projectName?: string;
  projectLocation?: string;
  reportData?: any;
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [navigationData, setNavigationData] = useState<NavigationData>({});

  const handleNavigation = (page: string, data?: any) => {
    setCurrentPage(page as Page);
    setNavigationData(data || {});
  };

  const handleProjectCreated = () => {
    setCurrentPage("projects");
  };

  const handleAnalyzeProject = (projectId: number, projectName: string) => {
    setNavigationData({ projectId, projectName });
    setCurrentPage("analysis");
  };

  const handleGeospatialAnalysis = (
    projectId: number,
    projectName: string,
    projectLocation: string
  ) => {
    setNavigationData({ projectId, projectName, projectLocation });
    setCurrentPage("geospatial");
  };

  const handleSustainabilityAnalysis = (
    projectId: number,
    projectName: string
  ) => {
    setNavigationData({ projectId, projectName });
    setCurrentPage("sustainability");
  };

  const handleIntegratedAnalysis = (
    projectId: number,
    projectName: string,
    projectLocation: string
  ) => {
    setNavigationData({ projectId, projectName, projectLocation });
    setCurrentPage("integrated");
  };

  return (
    <div className="App">
      {currentPage === "dashboard" && (
        <Dashboard onNavigate={handleNavigation} />
      )}

      {currentPage === "projects" && (
        <div
          style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          }}
        >
          <div
            style={{
              background: "rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(10px)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
              padding: "20px 40px",
              color: "white",
            }}
          >
            <button
              onClick={() => setCurrentPage("dashboard")}
              style={{
                padding: "10px 20px",
                backgroundColor: "rgba(244, 67, 54, 0.8)",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                marginRight: "20px",
                backdropFilter: "blur(10px)",
              }}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage("newProject")}
              style={{
                padding: "10px 20px",
                backgroundColor: "rgba(76, 175, 80, 0.8)",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                backdropFilter: "blur(10px)",
              }}
            >
              Nuevo Proyecto
            </button>
          </div>
          <div style={{ padding: "40px" }}>
            <ProjectList
              onAnalyze={handleAnalyzeProject}
              onGeospatialAnalysis={handleGeospatialAnalysis}
              onSustainabilityAnalysis={handleSustainabilityAnalysis}
              onIntegratedAnalysis={handleIntegratedAnalysis}
            />
          </div>
        </div>
      )}

      {currentPage === "newProject" && (
        <ProjectForm
          onSuccess={handleProjectCreated}
          onCancel={() => setCurrentPage("projects")}
        />
      )}

      {currentPage === "analysis" && navigationData.projectId && (
        <ProjectAnalysis
          projectId={navigationData.projectId}
          projectName={navigationData.projectName!}
          onBack={() => setCurrentPage("projects")}
        />
      )}

      {currentPage === "geospatial" && navigationData.projectId && (
        <GeospatialAnalysis
          projectId={navigationData.projectId}
          projectName={navigationData.projectName!}
          projectLocation={navigationData.projectLocation!}
          onBack={() => setCurrentPage("projects")}
        />
      )}

      {currentPage === "sustainability" && navigationData.projectId && (
        <SustainabilityAnalysis
          projectId={navigationData.projectId}
          projectName={navigationData.projectName!}
          onBack={() => setCurrentPage("projects")}
        />
      )}

      {currentPage === "integrated" && navigationData.projectId && (
        <IntegratedAnalysisDashboard
          projectId={navigationData.projectId}
          projectName={navigationData.projectName!}
          projectLocation={navigationData.projectLocation!}
          onBack={() => setCurrentPage("projects")}
          onNavigate={handleNavigation}
        />
      )}

      {currentPage === "reports" && navigationData.reportData && (
        <ReportGenerator
          reportData={navigationData.reportData}
          onBack={() => setCurrentPage("integrated")}
        />
      )}

      {currentPage === "comparison" && (
        <ProjectComparison onBack={() => setCurrentPage("dashboard")} />
      )}

      {currentPage === "advanced" && (
        <div
          style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
            padding: "40px",
            color: "white",
          }}
        >
          <button
            onClick={() => setCurrentPage("dashboard")}
            style={{
              padding: "12px 24px",
              background: "linear-gradient(135deg, #ff6b6b, #ee5a52)",
              color: "white",
              border: "none",
              borderRadius: "50px",
              cursor: "pointer",
              marginBottom: "30px",
            }}
          >
            ← Volver al Dashboard
          </button>
          <h2>Análisis Avanzado</h2>
          <p>Funcionalidad en desarrollo...</p>
        </div>
      )}
    </div>
  );
}

export default App;
