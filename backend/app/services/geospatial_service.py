from typing import List, Dict, Tuple, Optional
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import transform
import numpy as np
from dataclasses import dataclass
import math

@dataclass
class LayerRestriction:
    """Restricción por capa"""
    name: str
    type: str  # "exclusion", "limitation", "buffer"
    geometry: Polygon
    reduction_factor: float = 1.0  # Factor de reducción (1.0 = 100% permitido, 0.0 = 0% permitido)
    buffer_distance: float = 0.0  # Distancia de buffer en metros
    description: str = ""

@dataclass
class AnalysisResult:
    """Resultado del análisis geoespacial"""
    total_area: float
    buildable_area: float
    restricted_area: float
    buildability_percentage: float
    restrictions_applied: List[str]
    optimal_building_zones: List[Polygon]
    recommendations: List[str]

class GeospatialService:
    
    def __init__(self):
        self.restrictions_catalog = self._initialize_restrictions_catalog()
    
    def _initialize_restrictions_catalog(self) -> Dict:
        """Catálogo de restricciones típicas en desarrollo urbano"""
        return {
            "retiros_obligatorios": {
                "frontal": {"distance": 5, "description": "Retiro frontal mínimo"},
                "lateral": {"distance": 3, "description": "Retiro lateral mínimo"},  
                "posterior": {"distance": 5, "description": "Retiro posterior mínimo"}
            },
            "areas_protegidas": {
                "humedales": {"reduction_factor": 0.0, "buffer": 30},
                "rondas_hidraulicas": {"reduction_factor": 0.0, "buffer": 30},
                "zonas_verdes": {"reduction_factor": 0.2, "buffer": 0}
            },
            "infraestructura": {
                "redes_electricas": {"buffer": 10, "reduction_factor": 0.8},
                "tuberias_gas": {"buffer": 15, "reduction_factor": 0.0},
                "alcantarillado": {"buffer": 3, "reduction_factor": 0.9}
            },
            "normativa_urbana": {
                "indice_ocupacion": {"max_percentage": 0.7},
                "indice_construccion": {"max_ratio": 2.5},
                "altura_maxima": {"max_floors": 5}
            }
        }
    
    def calculate_area(self, polygon: Polygon) -> float:
        """Calcular área de polígono en metros cuadrados"""
        # Para coordenadas geográficas, usar proyección aproximada
        # En un sistema real, usaríamos pyproj para proyecciones exactas
        
        # Aproximación usando fórmula de Haversine para área
        coords = list(polygon.exterior.coords)
        n = len(coords) - 1  # Último punto es igual al primero
        
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            lat1, lon1 = coords[i][1], coords[i][0]
            lat2, lon2 = coords[j][1], coords[j][0]
            
            # Convertir a radianes
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lon = math.radians(lon2 - lon1)
            
            # Aproximación del área usando proyección local
            # Radio promedio de la Tierra en metros
            R = 6371000
            
            # Área aproximada del segmento
            segment_area = R * R * abs(delta_lon) * abs(math.sin(lat2_rad) - math.sin(lat1_rad))
            area += segment_area
        
        return abs(area)
    
    def apply_building_setbacks(
        self, 
        lot_polygon: Polygon, 
        setbacks: Dict[str, float]
    ) -> Polygon:
        """Aplicar retiros obligatorios al lote"""
        
        # Esta es una implementación simplificada
        # En un sistema real, se consideraría la orientación exacta del lote
        
        # Obtener el bounding box del lote
        minx, miny, maxx, maxy = lot_polygon.bounds
        
        # Aplicar retiros (simplificado)
        frontal = setbacks.get("frontal", 5)
        lateral = setbacks.get("lateral", 3)
        posterior = setbacks.get("posterior", 5)
        
        # Crear polígono con retiros aplicados
        # Esto es una simplificación - en la realidad se calcularía según la orientación
        buffer_distance = -min(frontal, lateral, posterior) * 0.00001  # Conversión aproximada a grados
        
        buildable_area = lot_polygon.buffer(buffer_distance)
        
        if buildable_area.is_empty:
            # Si el lote es muy pequeño, devolver un polígono mínimo
            center = lot_polygon.centroid
            min_buildable = Point(center.x, center.y).buffer(0.00005)  # 5m aprox
            return min_buildable
        
        return buildable_area
    
    def apply_environmental_restrictions(
        self, 
        buildable_polygon: Polygon,
        environmental_features: List[LayerRestriction]
    ) -> Polygon:
        """Aplicar restricciones ambientales"""
        
        current_polygon = buildable_polygon
        
        for restriction in environmental_features:
            if restriction.geometry.intersects(current_polygon):
                
                if restriction.type == "exclusion":
                    # Excluir completamente el área
                    current_polygon = current_polygon.difference(restriction.geometry)
                    
                elif restriction.type == "buffer":
                    # Aplicar buffer de restricción
                    buffer_area = restriction.geometry.buffer(
                        restriction.buffer_distance * 0.00001  # Conversión aproximada
                    )
                    current_polygon = current_polygon.difference(buffer_area)
                    
                elif restriction.type == "limitation":
                    # Aplicar factor de reducción
                    intersection = current_polygon.intersection(restriction.geometry)
                    if not intersection.is_empty:
                        # Reducir el área según el factor
                        reduced_intersection = intersection.buffer(
                            -intersection.area * (1 - restriction.reduction_factor) * 0.5
                        )
                        current_polygon = current_polygon.difference(intersection).union(reduced_intersection)
        
        return current_polygon if not current_polygon.is_empty else Point(0, 0).buffer(0.00001)
    
    def optimize_building_layout(
        self, 
        buildable_polygon: Polygon,
        building_requirements: Dict
    ) -> List[Polygon]:
        """Optimizar distribución de edificaciones en el área construible"""
        
        building_area = building_requirements.get("building_area", 100)  # m²
        max_buildings = building_requirements.get("max_buildings", 5)
        min_separation = building_requirements.get("min_separation", 6)  # metros
        
        optimal_zones = []
        
        # Dividir área construible en zonas potenciales
        bounds = buildable_polygon.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Calcular tamaño aproximado de cada edificación en coordenadas
        building_size_deg = math.sqrt(building_area) * 0.00001  # Aproximación
        separation_deg = min_separation * 0.00001
        
        # Crear grid de posiciones potenciales
        x_positions = np.arange(bounds[0] + building_size_deg, bounds[2] - building_size_deg, building_size_deg + separation_deg)
        y_positions = np.arange(bounds[1] + building_size_deg, bounds[3] - building_size_deg, building_size_deg + separation_deg)
        
        for x in x_positions:
            for y in y_positions:
                if len(optimal_zones) >= max_buildings:
                    break
                
                # Crear polígono de edificación candidata
                candidate_building = Point(x, y).buffer(building_size_deg)
                
                # Verificar si está completamente dentro del área construible
                if buildable_polygon.contains(candidate_building):
                    # Verificar separación con otras edificaciones
                    min_distance_ok = True
                    for existing in optimal_zones:
                        if candidate_building.distance(existing) < separation_deg:
                            min_distance_ok = False
                            break
                    
                    if min_distance_ok:
                        optimal_zones.append(candidate_building)
        
        return optimal_zones
    
    def analyze_terrain_suitability(
        self,
        lot_polygon: Polygon,
        terrain_data: Dict = None
    ) -> Dict:
        """Analizar idoneidad del terreno para construcción"""
        
        # Datos por defecto si no se proporcionan
        if terrain_data is None:
            terrain_data = {
                "slope_percentage": 5.0,
                "soil_type": "clay",
                "drainage": "good",
                "flood_risk": "low"
            }
        
        suitability_score = 100
        issues = []
        recommendations = []
        
        # Evaluar pendiente
        slope = terrain_data.get("slope_percentage", 0)
        if slope > 30:
            suitability_score -= 40
            issues.append("Pendiente muy pronunciada (>30%)")
            recommendations.append("Considerar terrazas o muros de contención")
        elif slope > 15:
            suitability_score -= 20
            issues.append("Pendiente moderada (15-30%)")
            recommendations.append("Diseño adaptado a la topografía")
        
        # Evaluar tipo de suelo
        soil_type = terrain_data.get("soil_type", "unknown")
        soil_penalties = {
            "sand": 10,
            "clay": 20,
            "rock": 30,
            "organic": 35,
            "fill": 40
        }
        
        if soil_type in soil_penalties:
            penalty = soil_penalties[soil_type]
            suitability_score -= penalty
            if penalty > 20:
                issues.append(f"Tipo de suelo problemático: {soil_type}")
                recommendations.append("Estudio geotécnico detallado requerido")
        
        # Evaluar drenaje
        drainage = terrain_data.get("drainage", "unknown")
        if drainage == "poor":
            suitability_score -= 25
            issues.append("Drenaje deficiente")
            recommendations.append("Sistema de drenaje mejorado necesario")
        
        # Evaluar riesgo de inundación
        flood_risk = terrain_data.get("flood_risk", "unknown")
        flood_penalties = {"high": 50, "medium": 25, "low": 0}
        if flood_risk in flood_penalties:
            penalty = flood_penalties[flood_risk]
            suitability_score -= penalty
            if penalty > 0:
                issues.append(f"Riesgo de inundación: {flood_risk}")
                recommendations.append("Considerar elevación de estructuras")
        
        return {
            "suitability_score": max(0, suitability_score),
            "suitability_level": self._get_suitability_level(suitability_score),
            "issues": issues,
            "recommendations": recommendations,
            "terrain_analysis": terrain_data
        }
    
    def _get_suitability_level(self, score: float) -> str:
        """Convertir puntaje a nivel de idoneidad"""
        if score >= 80:
            return "Excelente"
        elif score >= 60:
            return "Bueno"
        elif score >= 40:
            return "Regular"
        else:
            return "Problemático"
    
    def perform_complete_analysis(
        self,
        lot_polygon: Polygon,
        environmental_restrictions: List[LayerRestriction] = None,
        building_requirements: Dict = None,
        terrain_data: Dict = None
    ) -> AnalysisResult:
        """Realizar análisis geoespacial completo"""
        
        if environmental_restrictions is None:
            environmental_restrictions = []
        
        if building_requirements is None:
            building_requirements = {"building_area": 100, "max_buildings": 3}
        
        # 1. Calcular área total
        total_area = self.calculate_area(lot_polygon)
        
        # 2. Aplicar retiros obligatorios
        setbacks = self.restrictions_catalog["retiros_obligatorios"]
        buildable_with_setbacks = self.apply_building_setbacks(lot_polygon, {
            "frontal": setbacks["frontal"]["distance"],
            "lateral": setbacks["lateral"]["distance"], 
            "posterior": setbacks["posterior"]["distance"]
        })
        
        # 3. Aplicar restricciones ambientales
        final_buildable = self.apply_environmental_restrictions(
            buildable_with_setbacks, 
            environmental_restrictions
        )
        
        # 4. Calcular áreas finales
        buildable_area = self.calculate_area(final_buildable)
        restricted_area = total_area - buildable_area
        buildability_percentage = (buildable_area / total_area) * 100 if total_area > 0 else 0
        
        # 5. Optimizar distribución de edificaciones
        optimal_zones = self.optimize_building_layout(final_buildable, building_requirements)
        
        # 6. Analizar idoneidad del terreno
        terrain_analysis = self.analyze_terrain_suitability(lot_polygon, terrain_data)
        
        # 7. Generar recomendaciones
        recommendations = []
        restrictions_applied = []
        
        if buildability_percentage < 30:
            recommendations.append("Considerar reducir el número de edificaciones")
            recommendations.append("Evaluar modificación del diseño arquitectónico")
        
        if buildability_percentage > 80:
            recommendations.append("Excelente aprovechamiento del lote")
            recommendations.append("Considerar áreas verdes adicionales")
        
        if len(optimal_zones) < building_requirements.get("max_buildings", 3):
            recommendations.append("El diseño propuesto puede requerir ajustes")
            recommendations.append("Considerar edificaciones de mayor altura")
        
        # Agregar recomendaciones del análisis de terreno
        recommendations.extend(terrain_analysis["recommendations"])
        
        # Registrar restricciones aplicadas
        for restriction in environmental_restrictions:
            restrictions_applied.append(restriction.name)
        
        return AnalysisResult(
            total_area=total_area,
            buildable_area=buildable_area,
            restricted_area=restricted_area,
            buildability_percentage=buildability_percentage,
            restrictions_applied=restrictions_applied,
            optimal_building_zones=optimal_zones,
            recommendations=recommendations
        )
    
    def create_layers_for_visualization(
        self,
        lot_polygon: Polygon,
        analysis_result: AnalysisResult,
        environmental_restrictions: List[LayerRestriction] = None
    ) -> Dict:
        """Crear capas para visualización en frontend"""
        
        layers = {
            "lot_boundary": {
                "type": "polygon",
                "coordinates": list(lot_polygon.exterior.coords),
                "style": {"color": "#2563eb", "weight": 2, "fillOpacity": 0.1}
            },
            "buildable_areas": [],
            "restricted_areas": [],
            "optimal_buildings": [],
            "measurements": []
        }
        
        # Agregar zonas de edificaciones óptimas
        for i, building_zone in enumerate(analysis_result.optimal_building_zones):
            layers["optimal_buildings"].append({
                "type": "polygon",
                "coordinates": list(building_zone.exterior.coords),
                "style": {"color": "#16a34a", "weight": 2, "fillOpacity": 0.3},
                "popup": f"Edificación {i+1}"
            })
        
        # Agregar restricciones ambientales
        if environmental_restrictions:
            for restriction in environmental_restrictions:
                layers["restricted_areas"].append({
                    "type": "polygon",
                    "coordinates": list(restriction.geometry.exterior.coords),
                    "style": {"color": "#dc2626", "weight": 1, "fillOpacity": 0.2},
                    "popup": f"{restriction.name}: {restriction.description}"
                })
        
        # Agregar mediciones
        layers["measurements"] = [
            {
                "type": "text",
                "position": list(lot_polygon.centroid.coords)[0],
                "text": f"Área total: {analysis_result.total_area:.0f} m²"
            },
            {
                "type": "text", 
                "position": [lot_polygon.centroid.x, lot_polygon.centroid.y - 0.0001],
                "text": f"Área construible: {analysis_result.buildable_area:.0f} m²"
            },
            {
                "type": "text",
                "position": [lot_polygon.centroid.x, lot_polygon.centroid.y - 0.0002], 
                "text": f"Aprovechamiento: {analysis_result.buildability_percentage:.1f}%"
            }
        ]
        
        return layers