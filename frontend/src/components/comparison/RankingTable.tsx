// frontend/src/components/comparison/RankingTable.tsx
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface RankingTableProps {
  data: any;
  filters: any;
}

const RankingTable: React.FC<RankingTableProps> = ({ data, filters }) => {
  const [sortBy, setSortBy] = useState<
    "overall" | "npv" | "irr" | "sustainability"
  >("overall");

  const getSortedProjects = () => {
    const projectsWithScores = data.projects.map(
      (project: any, index: number) => ({
        ...project,
        metrics: data.metrics[index],
      })
    );

    return projectsWithScores.sort((a: any, b: any) => {
      switch (sortBy) {
        case "npv":
          return b.metrics.financial.npv - a.metrics.financial.npv;
        case "irr":
          return b.metrics.financial.irr - a.metrics.financial.irr;
        case "sustainability":
          return (
            b.metrics.sustainability.score - a.metrics.sustainability.score
          );
        default:
          return b.metrics.overall - a.metrics.overall;
      }
    });
  };

  const sortedProjects = getSortedProjects();

  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1:
        return "🥇";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return `#${rank}`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      style={{
        background: "rgba(255, 255, 255, 0.05)",
        backdropFilter: "blur(20px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "20px",
        padding: "30px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "25px",
        }}
      >
        <h3
          style={{
            color: "white",
            fontSize: "20px",
            fontWeight: "300",
          }}
        >
          🏆 Ranking de Proyectos
        </h3>

        <div style={{ display: "flex", gap: "10px" }}>
          {["overall", "npv", "irr", "sustainability"].map((criterion) => (
            <motion.button
              key={criterion}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSortBy(criterion as any)}
              style={{
                padding: "8px 16px",
                background:
                  sortBy === criterion
                    ? "linear-gradient(135deg, #8b5cf6, #7c3aed)"
                    : "rgba(255, 255, 255, 0.1)",
                color: "white",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "20px",
                cursor: "pointer",
                fontSize: "12px",
                transition: "all 0.3s ease",
              }}
            >
              {criterion === "overall"
                ? "General"
                : criterion === "npv"
                ? "VPN"
                : criterion === "irr"
                ? "TIR"
                : "Sostenibilidad"}
            </motion.button>
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={sortBy}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.3 }}
        >
          {sortedProjects.map((project: any, index: number) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              style={{
                display: "grid",
                gridTemplateColumns: "60px 1fr auto auto auto auto",
                alignItems: "center",
                gap: "20px",
                padding: "20px",
                marginBottom: "15px",
                background:
                  index === 0
                    ? "linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 193, 7, 0.05))"
                    : "rgba(255, 255, 255, 0.03)",
                border:
                  index === 0
                    ? "2px solid rgba(255, 215, 0, 0.3)"
                    : "1px solid rgba(255, 255, 255, 0.1)",
                borderRadius: "15px",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateX(10px)";
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateX(0)";
                e.currentTarget.style.background =
                  index === 0
                    ? "linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 193, 7, 0.05))"
                    : "rgba(255, 255, 255, 0.03)";
              }}
            >
              <div
                style={{
                  fontSize: "24px",
                  textAlign: "center",
                  fontWeight: "bold",
                }}
              >
                {getMedalEmoji(index + 1)}
              </div>

              <div>
                <h4
                  style={{
                    color: "white",
                    margin: "0 0 5px 0",
                    fontSize: "16px",
                    fontWeight: "500",
                  }}
                >
                  {project.name}
                </h4>
                <p
                  style={{
                    color: "rgba(255, 255, 255, 0.6)",
                    margin: 0,
                    fontSize: "12px",
                  }}
                >
                  {project.location}
                </p>
              </div>

              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    color: "#4ade80",
                    fontSize: "14px",
                    fontWeight: "600",
                  }}
                >
                  ${Math.round(project.metrics.financial.npv / 1000)}K
                </div>
                <div
                  style={{
                    color: "rgba(255, 255, 255, 0.5)",
                    fontSize: "10px",
                  }}
                >
                  VPN
                </div>
              </div>

              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    color: "#3b82f6",
                    fontSize: "14px",
                    fontWeight: "600",
                  }}
                >
                  {(project.metrics.financial.irr * 100).toFixed(1)}%
                </div>
                <div
                  style={{
                    color: "rgba(255, 255, 255, 0.5)",
                    fontSize: "10px",
                  }}
                >
                  TIR
                </div>
              </div>

              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    color: "#10b981",
                    fontSize: "14px",
                    fontWeight: "600",
                  }}
                >
                  {project.metrics.sustainability.score.toFixed(1)}
                </div>
                <div
                  style={{
                    color: "rgba(255, 255, 255, 0.5)",
                    fontSize: "10px",
                  }}
                >
                  Sostenib.
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "10px 20px",
                  background:
                    "linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(147, 51, 234, 0.1))",
                  borderRadius: "50px",
                  border: "1px solid rgba(139, 92, 246, 0.3)",
                }}
              >
                <span
                  style={{
                    color: "#8b5cf6",
                    fontSize: "18px",
                    fontWeight: "bold",
                  }}
                >
                  {project.metrics.overall.toFixed(1)}
                </span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>

      {/* Resumen del ganador */}
      {sortedProjects.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          style={{
            marginTop: "30px",
            padding: "25px",
            background:
              "linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(147, 51, 234, 0.05))",
            border: "1px solid rgba(139, 92, 246, 0.3)",
            borderRadius: "15px",
            textAlign: "center",
          }}
        >
          <h4 style={{ color: "#8b5cf6", marginBottom: "10px" }}>
            🎉 Proyecto Recomendado
          </h4>
          <p style={{ color: "white", fontSize: "18px", fontWeight: "500" }}>
            {sortedProjects[0].name}
          </p>
          <p
            style={{
              color: "rgba(255, 255, 255, 0.7)",
              fontSize: "14px",
              marginTop: "10px",
            }}
          >
            Basado en el criterio:{" "}
            {sortBy === "overall"
              ? "Evaluación General"
              : sortBy === "npv"
              ? "Valor Presente Neto"
              : sortBy === "irr"
              ? "Tasa Interna de Retorno"
              : "Sostenibilidad"}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default RankingTable;