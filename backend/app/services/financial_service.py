import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy.optimize import minimize_scalar
import numpy_financial as npf

@dataclass
class ProjectFinancials:
    """Datos financieros del proyecto"""
    terrain_cost: float
    construction_cost_per_m2: float
    total_area: float
    buildable_area: float
    selling_price_per_m2: float
    construction_time_months: int
    selling_time_months: int
    discount_rate: float  # Tasa de descuento anual
    financing_rate: float = 0.0  # Tasa de financiamiento
    financing_percentage: float = 0.0  # Porcentaje de financiamiento

@dataclass
class SensitivityParameters:
    """Parámetros para análisis de sensibilidad"""
    construction_cost_range: Tuple[float, float] = (-0.2, 0.3)  # -20% a +30%
    selling_price_range: Tuple[float, float] = (-0.15, 0.25)   # -15% a +25%
    construction_time_range: Tuple[int, int] = (-3, 6)         # -3 a +6 meses
    selling_time_range: Tuple[int, int] = (-6, 12)            # -6 a +12 meses

class FinancialService:
    
    def __init__(self):
        pass
    
    def calculate_basic_metrics(self, project: ProjectFinancials) -> Dict:
        """Calcular métricas financieras básicas"""
        
        # Costos
        total_terrain_cost = project.terrain_cost
        total_construction_cost = project.buildable_area * project.construction_cost_per_m2
        total_cost = total_terrain_cost + total_construction_cost
        
        # Ingresos
        total_revenue = project.buildable_area * project.selling_price_per_m2
        
        # Métricas básicas
        gross_profit = total_revenue - total_cost
        profit_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
        roi = (gross_profit / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            "costs": {
                "terrain_cost": total_terrain_cost,
                "construction_cost": total_construction_cost,
                "total_cost": total_cost,
                "cost_per_m2": total_cost / project.buildable_area if project.buildable_area > 0 else 0
            },
            "revenue": {
                "total_revenue": total_revenue,
                "revenue_per_m2": project.selling_price_per_m2
            },
            "profitability": {
                "gross_profit": gross_profit,
                "profit_margin_percentage": profit_margin,
                "roi_percentage": roi
            }
        }
    
    def calculate_npv_irr(self, project: ProjectFinancials) -> Dict:
        """Calcular VPN (NPV) y TIR (IRR)"""
        
        # Crear flujo de caja mensual
        total_months = project.construction_time_months + project.selling_time_months
        cash_flows = np.zeros(total_months + 1)  # +1 para mes 0
        
        # Inversión inicial (mes 0)
        cash_flows[0] = -project.terrain_cost
        
        # Costos de construcción distribuidos durante tiempo de construcción
        monthly_construction_cost = (
            project.buildable_area * project.construction_cost_per_m2
        ) / project.construction_time_months
        
        for month in range(1, project.construction_time_months + 1):
            cash_flows[month] = -monthly_construction_cost
        
        # Ingresos por ventas distribuidos durante tiempo de venta
        total_revenue = project.buildable_area * project.selling_price_per_m2
        monthly_revenue = total_revenue / project.selling_time_months
        
        start_selling = project.construction_time_months + 1
        for month in range(start_selling, total_months + 1):
            cash_flows[month] = monthly_revenue
        
        # Convertir tasa anual a mensual
        monthly_rate = project.discount_rate / 12
        
        # Calcular NPV
        npv = npf.npv(monthly_rate, cash_flows)
        
        # Calcular IRR
        try:
            irr_monthly = npf.irr(cash_flows)
            irr_annual = (1 + irr_monthly) ** 12 - 1 if irr_monthly is not None else None
        except:
            irr_annual = None
        
        return {
            "npv": npv,
            "irr_annual": irr_annual,
            "irr_monthly": irr_monthly if 'irr_monthly' in locals() else None,
            "cash_flows": cash_flows.tolist(),
            "months": list(range(len(cash_flows)))
        }
    
    def perform_sensitivity_analysis(
        self, 
        project: ProjectFinancials, 
        params: SensitivityParameters = None
    ) -> Dict:
        """Realizar análisis de sensibilidad"""
        
        if params is None:
            params = SensitivityParameters()
        
        results = {
            "base_case": {},
            "scenarios": [],
            "sensitivity_matrix": {}
        }
        
        # Caso base
        base_metrics = self.calculate_npv_irr(project)
        results["base_case"] = {
            "npv": base_metrics["npv"],
            "irr": base_metrics["irr_annual"]
        }
        
        # Variables a analizar
        variables = [
            ("construction_cost", params.construction_cost_range, "construction_cost_per_m2"),
            ("selling_price", params.selling_price_range, "selling_price_per_m2"),
            ("construction_time", params.construction_time_range, "construction_time_months"),
            ("selling_time", params.selling_time_range, "selling_time_months")
        ]
        
        # Análisis univariado
        for var_name, var_range, attr_name in variables:
            scenarios = []
            
            # Crear 5 escenarios por variable
            if var_name in ["construction_time", "selling_time"]:
                # Para tiempo, usar valores enteros
                values = np.linspace(var_range[0], var_range[1], 5, dtype=int)
            else:
                # Para porcentajes
                values = np.linspace(var_range[0], var_range[1], 5)
            
            for value in values:
                # Crear copia del proyecto
                test_project = ProjectFinancials(**project.__dict__)
                
                if var_name in ["construction_time", "selling_time"]:
                    # Sumar/restar meses
                    original_value = getattr(test_project, attr_name)
                    setattr(test_project, attr_name, max(1, original_value + value))
                else:
                    # Aplicar porcentaje
                    original_value = getattr(test_project, attr_name)
                    setattr(test_project, attr_name, original_value * (1 + value))
                
                # Calcular métricas
                metrics = self.calculate_npv_irr(test_project)
                basic_metrics = self.calculate_basic_metrics(test_project)
                
                scenarios.append({
                    "variable": var_name,
                    "change_percentage": value * 100 if var_name not in ["construction_time", "selling_time"] else value,
                    "npv": metrics["npv"],
                    "irr": metrics["irr_annual"],
                    "roi": basic_metrics["profitability"]["roi_percentage"]
                })
            
            results["scenarios"].extend(scenarios)
        
        return results
    
    def optimize_project(self, project: ProjectFinancials, optimization_target: str = "npv") -> Dict:
        """Optimizar proyecto para maximizar objetivo"""
        
        def objective_function(selling_price_multiplier):
            """Función objetivo para optimización"""
            test_project = ProjectFinancials(**project.__dict__)
            test_project.selling_price_per_m2 *= selling_price_multiplier
            
            if optimization_target == "npv":
                return -self.calculate_npv_irr(test_project)["npv"]  # Negativo para maximizar
            elif optimization_target == "roi":
                return -self.calculate_basic_metrics(test_project)["profitability"]["roi_percentage"]
            else:
                return 0
        
        # Optimizar precio de venta (entre 0.8 y 2.0 del precio base)
        result = minimize_scalar(
            objective_function,
            bounds=(0.8, 2.0),
            method='bounded'
        )
        
        # Crear proyecto optimizado
        optimized_project = ProjectFinancials(**project.__dict__)
        optimized_project.selling_price_per_m2 *= result.x
        
        optimized_metrics = self.calculate_npv_irr(optimized_project)
        optimized_basic = self.calculate_basic_metrics(optimized_project)
        
        return {
            "optimal_selling_price_multiplier": result.x,
            "optimal_selling_price_per_m2": optimized_project.selling_price_per_m2,
            "optimized_metrics": {
                "npv": optimized_metrics["npv"],
                "irr": optimized_metrics["irr_annual"],
                "roi": optimized_basic["profitability"]["roi_percentage"]
            },
            "improvement": {
                "npv_improvement": optimized_metrics["npv"] - self.calculate_npv_irr(project)["npv"],
                "roi_improvement": optimized_basic["profitability"]["roi_percentage"] - self.calculate_basic_metrics(project)["profitability"]["roi_percentage"]
            }
        }
    
    def create_financial_report(self, project: ProjectFinancials) -> Dict:
        """Crear reporte financiero completo"""
        
        basic_metrics = self.calculate_basic_metrics(project)
        npv_irr = self.calculate_npv_irr(project)
        sensitivity = self.perform_sensitivity_analysis(project)
        optimization = self.optimize_project(project)
        
        return {
            "project_summary": {
                "total_area": project.total_area,
                "buildable_area": project.buildable_area,
                "construction_time_months": project.construction_time_months,
                "selling_time_months": project.selling_time_months
            },
            "basic_metrics": basic_metrics,
            "advanced_metrics": npv_irr,
            "sensitivity_analysis": sensitivity,
            "optimization_results": optimization,
            "risk_assessment": self._assess_risk(project, npv_irr, sensitivity)
        }
    
    def _assess_risk(self, project: ProjectFinancials, npv_data: Dict, sensitivity_data: Dict) -> Dict:
        """Evaluar riesgo del proyecto"""
        
        risk_factors = []
        risk_score = 0  # 0-100, donde 100 es más riesgo
        
        # Evaluar TIR vs tasa de descuento
        if npv_data["irr_annual"] and npv_data["irr_annual"] < project.discount_rate * 1.5:
            risk_factors.append("TIR baja respecto a tasa de descuento")
            risk_score += 20
        
        # Evaluar VPN
        if npv_data["npv"] < 0:
            risk_factors.append("VPN negativo")
            risk_score += 30
        
        # Evaluar tiempo del proyecto
        total_time = project.construction_time_months + project.selling_time_months
        if total_time > 36:  # Más de 3 años
            risk_factors.append("Proyecto de larga duración")
            risk_score += 15
        
        # Evaluar sensibilidad
        # (Análisis más detallado de la variabilidad en los escenarios)
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": "Alto" if risk_score > 60 else "Medio" if risk_score > 30 else "Bajo",
            "risk_factors": risk_factors
        }