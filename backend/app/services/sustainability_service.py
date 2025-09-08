from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

class SustainabilityCategory(Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    ECONOMIC = "economic"
    GOVERNANCE = "governance"

@dataclass
class SustainabilityMetric:
    name: str
    category: SustainabilityCategory
    weight: float
    score: float
    max_score: float
    description: str
    recommendations: List[str]

@dataclass
class ProjectSustainability:
    total_score: float
    max_possible_score: float
    percentage: float
    category_scores: Dict[str, float]
    metrics: List[SustainabilityMetric]
    sustainability_level: str
    carbon_footprint: Dict
    certifications_eligible: List[str]
    improvement_opportunities: List[str]

class SustainabilityService:
    
    def __init__(self):
        self.certification_standards = self._initialize_certifications()
        self.carbon_factors = self._initialize_carbon_factors()
    
    def _initialize_certifications(self) -> Dict:
        """Estándares de certificación sostenible"""
        return {
            "LEED": {
                "minimum_score": 70,
                "categories": ["energy", "water", "materials", "indoor_quality", "innovation"],
                "description": "Leadership in Energy and Environmental Design"
            },
            "BREEAM": {
                "minimum_score": 65,
                "categories": ["management", "health", "energy", "transport", "water", "materials", "waste", "pollution", "ecology"],
                "description": "Building Research Establishment Environmental Assessment Method"
            },
            "CASA_COLOMBIA": {
                "minimum_score": 60,
                "categories": ["energy", "water", "materials", "quality", "location"],
                "description": "Certificación Ambiental Sostenible para las Américas - Colombia"
            },
            "EDGE": {
                "minimum_score": 55,
                "categories": ["energy", "water", "materials"],
                "description": "Excellence in Design for Greater Efficiencies"
            }
        }
    
    def _initialize_carbon_factors(self) -> Dict:
        """Factores de emisión de carbono por material y proceso"""
        return {
            "materials": {
                "concrete": 0.11,  # kg CO2/kg
                "steel": 1.85,
                "brick": 0.24,
                "wood": -0.45,  # Negativo por captura de carbono
                "aluminum": 8.24,
                "glass": 0.85
            },
            "energy": {
                "electricity_colombia": 0.164,  # kg CO2/kWh (promedio Colombia)
                "natural_gas": 0.185,  # kg CO2/kWh
                "diesel": 0.267,  # kg CO2/kWh
                "solar": 0.041,  # kg CO2/kWh
                "wind": 0.011   # kg CO2/kWh
            },
            "transport": {
                "construction_truck": 0.62,  # kg CO2/km
                "worker_commute": 0.12,  # kg CO2/km per person
                "material_transport": 0.089  # kg CO2/ton-km
            }
        }
    
    def evaluate_environmental_impact(self, project_data: Dict) -> Dict[str, SustainabilityMetric]:
        """Evaluar impacto ambiental"""
        
        metrics = {}
        
        # 1. Eficiencia Energética
        energy_efficiency = self._calculate_energy_efficiency(project_data)
        metrics["energy_efficiency"] = SustainabilityMetric(
            name="Eficiencia Energética",
            category=SustainabilityCategory.ENVIRONMENTAL,
            weight=0.25,
            score=energy_efficiency["score"],
            max_score=100,
            description="Evaluación del consumo energético proyectado",
            recommendations=energy_efficiency["recommendations"]
        )
        
        # 2. Gestión de Agua
        water_management = self._calculate_water_efficiency(project_data)
        metrics["water_management"] = SustainabilityMetric(
            name="Gestión del Agua",
            category=SustainabilityCategory.ENVIRONMENTAL,
            weight=0.20,
            score=water_management["score"],
            max_score=100,
            description="Eficiencia en el uso y tratamiento del agua",
            recommendations=water_management["recommendations"]
        )
        
        # 3. Materiales Sostenibles
        materials_score = self._evaluate_materials(project_data)
        metrics["sustainable_materials"] = SustainabilityMetric(
            name="Materiales Sostenibles",
            category=SustainabilityCategory.ENVIRONMENTAL,
            weight=0.20,
            score=materials_score["score"],
            max_score=100,
            description="Uso de materiales con bajo impacto ambiental",
            recommendations=materials_score["recommendations"]
        )
        
        # 4. Biodiversidad y Ecosistemas
        biodiversity_score = self._evaluate_biodiversity_impact(project_data)
        metrics["biodiversity"] = SustainabilityMetric(
            name="Protección de Biodiversidad",
            category=SustainabilityCategory.ENVIRONMENTAL,
            weight=0.15,
            score=biodiversity_score["score"],
            max_score=100,
            description="Impacto en ecosistemas locales",
            recommendations=biodiversity_score["recommendations"]
        )
        
        # 5. Gestión de Residuos
        waste_score = self._evaluate_waste_management(project_data)
        metrics["waste_management"] = SustainabilityMetric(
            name="Gestión de Residuos",
            category=SustainabilityCategory.ENVIRONMENTAL,
            weight=0.20,
            score=waste_score["score"],
            max_score=100,
            description="Estrategias de reducción y manejo de residuos",
            recommendations=waste_score["recommendations"]
        )
        
        return metrics
    
    def evaluate_social_impact(self, project_data: Dict) -> Dict[str, SustainabilityMetric]:
        """Evaluar impacto social"""
        
        metrics = {}
        
        # 1. Accesibilidad Universal
        accessibility_score = self._evaluate_accessibility(project_data)
        metrics["accessibility"] = SustainabilityMetric(
            name="Accesibilidad Universal",
            category=SustainabilityCategory.SOCIAL,
            weight=0.25,
            score=accessibility_score["score"],
            max_score=100,
            description="Diseño inclusivo para todas las personas",
            recommendations=accessibility_score["recommendations"]
        )
        
        # 2. Calidad del Ambiente Interior
        indoor_quality = self._evaluate_indoor_quality(project_data)
        metrics["indoor_quality"] = SustainabilityMetric(
            name="Calidad Ambiente Interior",
            category=SustainabilityCategory.SOCIAL,
            weight=0.20,
            score=indoor_quality["score"],
            max_score=100,
            description="Confort térmico, acústico y calidad del aire",
            recommendations=indoor_quality["recommendations"]
        )
        
        # 3. Conectividad y Transporte
        connectivity_score = self._evaluate_connectivity(project_data)
        metrics["connectivity"] = SustainabilityMetric(
            name="Conectividad y Transporte",
            category=SustainabilityCategory.SOCIAL,
            weight=0.25,
            score=connectivity_score["score"],
            max_score=100,
            description="Acceso a transporte público y servicios",
            recommendations=connectivity_score["recommendations"]
        )
        
        # 4. Espacios Comunitarios
        community_score = self._evaluate_community_spaces(project_data)
        metrics["community_spaces"] = SustainabilityMetric(
            name="Espacios Comunitarios",
            category=SustainabilityCategory.SOCIAL,
            weight=0.20,
            score=community_score["score"],
            max_score=100,
            description="Áreas de interacción social y recreación",
            recommendations=community_score["recommendations"]
        )
        
        # 5. Impacto en Comunidad Local
        local_impact = self._evaluate_local_impact(project_data)
        metrics["local_impact"] = SustainabilityMetric(
            name="Impacto en Comunidad Local",
            category=SustainabilityCategory.SOCIAL,
            weight=0.10,
            score=local_impact["score"],
            max_score=100,
            description="Beneficios para la comunidad existente",
            recommendations=local_impact["recommendations"]
        )
        
        return metrics
    
    def evaluate_economic_sustainability(self, project_data: Dict) -> Dict[str, SustainabilityMetric]:
        """Evaluar sostenibilidad económica"""
        
        metrics = {}
        
        # 1. Costos de Operación
        operational_costs = self._evaluate_operational_efficiency(project_data)
        metrics["operational_efficiency"] = SustainabilityMetric(
            name="Eficiencia Operacional",
            category=SustainabilityCategory.ECONOMIC,
            weight=0.30,
            score=operational_costs["score"],
            max_score=100,
            description="Costos de operación y mantenimiento a largo plazo",
            recommendations=operational_costs["recommendations"]
        )
        
        # 2. Valor a Largo Plazo
        long_term_value = self._evaluate_long_term_value(project_data)
        metrics["long_term_value"] = SustainabilityMetric(
            name="Valor a Largo Plazo",
            category=SustainabilityCategory.ECONOMIC,
            weight=0.25,
            score=long_term_value["score"],
            max_score=100,
            description="Apreciación y durabilidad del proyecto",
            recommendations=long_term_value["recommendations"]
        )
        
        # 3. Empleo Local
        local_employment = self._evaluate_local_employment(project_data)
        metrics["local_employment"] = SustainabilityMetric(
            name="Generación de Empleo Local",
            category=SustainabilityCategory.ECONOMIC,
            weight=0.20,
            score=local_employment["score"],
            max_score=100,
            description="Oportunidades de empleo para la comunidad local",
            recommendations=local_employment["recommendations"]
        )
        
        # 4. Innovación y Tecnología
        innovation_score = self._evaluate_innovation(project_data)
        metrics["innovation"] = SustainabilityMetric(
            name="Innovación y Tecnología",
            category=SustainabilityCategory.ECONOMIC,
            weight=0.25,
            score=innovation_score["score"],
            max_score=100,
            description="Uso de tecnologías avanzadas y innovadoras",
            recommendations=innovation_score["recommendations"]
        )
        
        return metrics
    
    def calculate_carbon_footprint(self, project_data: Dict) -> Dict:
        """Calcular huella de carbono del proyecto"""
        
        construction_emissions = 0
        operational_emissions = 0
        
        # Emisiones por materiales de construcción
        materials = project_data.get("materials", {})
        for material, quantity in materials.items():
            if material in self.carbon_factors["materials"]:
                factor = self.carbon_factors["materials"][material]
                construction_emissions += quantity * factor
        
        # Emisiones operacionales anuales
        energy_consumption = project_data.get("annual_energy_kwh", 0)
        energy_source = project_data.get("energy_source", "electricity_colombia")
        
        if energy_source in self.carbon_factors["energy"]:
            operational_emissions = energy_consumption * self.carbon_factors["energy"][energy_source]
        
        # Emisiones por transporte durante construcción
        transport_emissions = self._calculate_transport_emissions(project_data)
        
        total_construction = construction_emissions + transport_emissions
        
        return {
            "construction_phase": {
                "materials": construction_emissions,
                "transport": transport_emissions,
                "total": total_construction
            },
            "operational_annual": operational_emissions,
            "operational_50_years": operational_emissions * 50,
            "total_lifecycle": total_construction + (operational_emissions * 50),
            "carbon_intensity": {
                "per_m2": (total_construction + operational_emissions * 50) / project_data.get("total_area", 1),
                "per_unit": (total_construction + operational_emissions * 50) / project_data.get("number_of_units", 1)
            }
        }
    
    def evaluate_certification_eligibility(self, all_metrics: Dict[str, SustainabilityMetric]) -> List[str]:
        """Evaluar elegibilidad para certificaciones"""
        
        eligible_certifications = []
        
        # Calcular puntaje total
        total_score = sum(metric.score * metric.weight for metric in all_metrics.values())
        
        for cert_name, cert_requirements in self.certification_standards.items():
            if total_score >= cert_requirements["minimum_score"]:
                eligible_certifications.append(cert_name)
        
        return eligible_certifications
    
    def generate_sustainability_report(self, project_data: Dict) -> ProjectSustainability:
        """Generar reporte completo de sostenibilidad"""
        
        # Evaluar todas las categorías
        environmental_metrics = self.evaluate_environmental_impact(project_data)
        social_metrics = self.evaluate_social_impact(project_data)
        economic_metrics = self.evaluate_economic_sustainability(project_data)
        
        # Combinar todas las métricas
        all_metrics = {**environmental_metrics, **social_metrics, **economic_metrics}
        
        # Calcular puntajes por categoría
        category_scores = {}
        for category in SustainabilityCategory:
            category_metrics = [m for m in all_metrics.values() if m.category == category]
            if category_metrics:
                weighted_score = sum(m.score * m.weight for m in category_metrics)
                total_weight = sum(m.weight for m in category_metrics)
                category_scores[category.value] = weighted_score / total_weight if total_weight > 0 else 0
        
        # Calcular puntaje total
        total_score = sum(metric.score * metric.weight for metric in all_metrics.values())
        max_possible = sum(metric.max_score * metric.weight for metric in all_metrics.values())
        percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
        
        # Determinar nivel de sostenibilidad
        if percentage >= 85:
            sustainability_level = "Excelente"
        elif percentage >= 70:
            sustainability_level = "Muy Bueno"
        elif percentage >= 55:
            sustainability_level = "Bueno"
        elif percentage >= 40:
            sustainability_level = "Regular"
        else:
            sustainability_level = "Deficiente"
        
        # Calcular huella de carbono
        carbon_footprint = self.calculate_carbon_footprint(project_data)
        
        # Evaluar certificaciones elegibles
        certifications = self.evaluate_certification_eligibility(all_metrics)
        
        # Generar oportunidades de mejora
        improvement_opportunities = self._generate_improvement_opportunities(all_metrics)
        
        return ProjectSustainability(
            total_score=total_score,
            max_possible_score=max_possible,
            percentage=percentage,
            category_scores=category_scores,
            metrics=list(all_metrics.values()),
            sustainability_level=sustainability_level,
            carbon_footprint=carbon_footprint,
            certifications_eligible=certifications,
            improvement_opportunities=improvement_opportunities
        )
    
    # Métodos auxiliares de evaluación (implementación simplificada)
    def _calculate_energy_efficiency(self, project_data: Dict) -> Dict:
        base_score = 60
        recommendations = ["Implementar sistemas LED", "Considerar paneles solares"]
        
        if project_data.get("solar_panels", False):
            base_score += 20
        if project_data.get("led_lighting", False):
            base_score += 10
        if project_data.get("smart_systems", False):
            base_score += 10
            
        return {"score": min(base_score, 100), "recommendations": recommendations}
    
    def _calculate_water_efficiency(self, project_data: Dict) -> Dict:
        base_score = 50
        recommendations = ["Instalar sistemas de recolección de agua lluvia", "Usar plantas nativas"]
        
        if project_data.get("rainwater_collection", False):
            base_score += 25
        if project_data.get("greywater_recycling", False):
            base_score += 15
        if project_data.get("native_plants", False):
            base_score += 10
            
        return {"score": min(base_score, 100), "recommendations": recommendations}
    
    def _evaluate_materials(self, project_data: Dict) -> Dict:
        base_score = 55
        recommendations = ["Usar materiales locales", "Considerar materiales reciclados"]
        
        if project_data.get("local_materials", False):
            base_score += 20
        if project_data.get("recycled_materials", False):
            base_score += 15
        if project_data.get("certified_wood", False):
            base_score += 10
            
        return {"score": min(base_score, 100), "recommendations": recommendations}
    
    def _evaluate_biodiversity_impact(self, project_data: Dict) -> Dict:
        base_score = 60
        recommendations = ["Preservar vegetación existente", "Crear corredores verdes"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_waste_management(self, project_data: Dict) -> Dict:
        base_score = 50
        recommendations = ["Plan de gestión de residuos de construcción", "Áreas de compostaje"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_accessibility(self, project_data: Dict) -> Dict:
        base_score = 70
        recommendations = ["Rampas de acceso", "Ascensores accesibles"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_indoor_quality(self, project_data: Dict) -> Dict:
        base_score = 65
        recommendations = ["Ventilación natural", "Materiales con bajas emisiones"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_connectivity(self, project_data: Dict) -> Dict:
        base_score = 60
        recommendations = ["Acceso a transporte público", "Ciclovías"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_community_spaces(self, project_data: Dict) -> Dict:
        base_score = 55
        recommendations = ["Áreas recreativas", "Espacios de encuentro"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_local_impact(self, project_data: Dict) -> Dict:
        base_score = 60
        recommendations = ["Contratación de mano de obra local", "Apoyo a comercio local"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_operational_efficiency(self, project_data: Dict) -> Dict:
        base_score = 65
        recommendations = ["Sistemas automatizados", "Mantenimiento preventivo"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_long_term_value(self, project_data: Dict) -> Dict:
        base_score = 70
        recommendations = ["Materiales durables", "Diseño adaptable"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_local_employment(self, project_data: Dict) -> Dict:
        base_score = 55
        recommendations = ["Capacitación laboral local", "Alianzas con instituciones educativas"]
        return {"score": base_score, "recommendations": recommendations}
    
    def _evaluate_innovation(self, project_data: Dict) -> Dict:
        base_score = 50
        recommendations = ["Tecnología BIM", "Sistemas inteligentes"]
        
        if project_data.get("bim_technology", False):
            base_score += 15
        if project_data.get("iot_systems", False):
            base_score += 20
        if project_data.get("renewable_energy", False):
            base_score += 15
            
        return {"score": min(base_score, 100), "recommendations": recommendations}
    
    def _calculate_transport_emissions(self, project_data: Dict) -> float:
        """Calcular emisiones por transporte durante construcción"""
        construction_duration_months = project_data.get("construction_duration_months", 12)
        site_distance_km = project_data.get("average_transport_distance_km", 25)
        
        # Estimación de viajes de construcción
        daily_trips = 10  # Aproximado
        working_days = construction_duration_months * 22  # 22 días laborales por mes
        total_trips = daily_trips * working_days
        
        emissions = total_trips * site_distance_km * self.carbon_factors["transport"]["construction_truck"]
        return emissions
    
    def _generate_improvement_opportunities(self, metrics: Dict[str, SustainabilityMetric]) -> List[str]:
        """Generar oportunidades de mejora basadas en puntajes bajos"""
        
        opportunities = []
        
        # Identificar métricas con puntajes bajos
        low_scoring_metrics = [m for m in metrics.values() if m.score < 60]
        
        # Ordenar por impacto potencial (peso * brecha de puntaje)
        low_scoring_metrics.sort(key=lambda x: x.weight * (100 - x.score), reverse=True)
        
        for metric in low_scoring_metrics[:5]:  # Top 5 oportunidades
            gap = 100 - metric.score
            potential_impact = gap * metric.weight
            
            opportunity = f"Mejorar {metric.name}: potencial de incremento de {gap:.1f} puntos " \
                         f"(impacto ponderado: {potential_impact:.1f})"
            
            opportunities.append(opportunity)
        
        return opportunities