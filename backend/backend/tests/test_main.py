"""
Tests básicos para GeoProfit Analytics
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "GeoProfit Analytics API"
    assert "version" in data
    assert "features" in data

def test_health_check():
    """Test del health check"""
    response = client.get("/health")
    # Puede dar error si no hay base de datos configurada, pero debe responder
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data

def test_api_info():
    """Test del endpoint de información"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "api_name" in data
    assert "endpoints" in data
    assert "external_integrations" in data

def test_create_project_validation():
    """Test de validación al crear proyecto"""
    # Test con datos inválidos
    invalid_project = {
        "name": "",  # Nombre vacío
        "location": "Test Location",
        "zone_type": "residential",
        "total_area": -100,  # Área negativa
        "terrain_value": 0,
        "construction_cost_per_m2": 0,
        "investment_horizon": 0
    }
    
    response = client.post("/projects/", json=invalid_project)
    assert response.status_code == 422  # Validation error

def test_projects_list_empty():
    """Test de listado de proyectos (puede estar vacío)"""
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data