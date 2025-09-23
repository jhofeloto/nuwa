"""
Test suite for ML integration and CO2 prediction functionality
"""

import pytest
import requests
import json
import asyncio
from typing import Dict, Any

# Test configuration
BASE_URL = "https://8002-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev"

class TestMLIntegration:
    """Test cases for ML integration endpoints"""
    
    def test_health_check_includes_ml(self):
        """Test that health check reports ML status"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "services" in health_data
        assert "ml_models" in health_data["services"]
        assert health_data["services"]["ml_models"] == "initialized"
    
    def test_ml_model_status(self):
        """Test ML model status endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/ml/model-status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["success"] == True
        assert "ml_models" in status_data
        assert status_data["ml_models"]["status"] == "trained"
        assert len(status_data["ml_models"]["models"]) == 3
        
        # Check that all expected models are present
        expected_models = ["random_forest", "gradient_boosting", "linear_regression"]
        actual_models = status_data["ml_models"]["models"]
        for model in expected_models:
            assert model in actual_models
        
        # Check performance metrics
        metrics = status_data["ml_models"]["metrics"]
        for model in expected_models:
            assert model in metrics
            assert "r2" in metrics[model]
            assert "rmse" in metrics[model]
            assert metrics[model]["r2"] > 0.6  # Minimum acceptable R²
    
    def test_co2_prediction_basic(self):
        """Test basic CO2 prediction functionality"""
        test_project = {
            "area_hectares": 1000,
            "duration_years": 10,
            "budget_usd": 500000,
            "climate_zone": "tropical",
            "vegetation_type": "forest",
            "methodology": "afforestation",
            "soil_type": "clay",
            "annual_rainfall_mm": 2000,
            "avg_temperature_c": 25,
            "elevation_m": 500,
            "latitude": -5.5,
            "longitude": -55.0,
            "technology_level": "high"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict-co2",
            json=test_project,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        
        prediction_data = response.json()
        assert prediction_data["success"] == True
        assert "prediction" in prediction_data
        
        prediction = prediction_data["prediction"]
        assert "predicted_co2_tons_year" in prediction
        assert prediction["predicted_co2_tons_year"] > 0
        assert "confidence_interval_lower" in prediction
        assert "confidence_interval_upper" in prediction
        assert "individual_predictions" in prediction
        
        # Check individual model predictions
        individual = prediction["individual_predictions"]
        assert "random_forest" in individual
        assert "gradient_boosting" in individual
        assert "linear_regression" in individual
    
    def test_co2_prediction_edge_cases(self):
        """Test CO2 prediction with edge cases"""
        # Test with minimal data
        minimal_project = {"area_hectares": 1}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict-co2",
            json=minimal_project,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        prediction_data = response.json()
        assert prediction_data["success"] == True
        
        # Test with missing required field
        invalid_project = {"duration_years": 10}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict-co2",
            json=invalid_project,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400  # Should return validation error
    
    def test_enhance_existing_project(self):
        """Test enhancing existing project with ML"""
        response = requests.post(f"{BASE_URL}/api/v1/ml/enhance-project/1")
        
        assert response.status_code == 200
        
        enhancement_data = response.json()
        assert enhancement_data["success"] == True
        assert "project" in enhancement_data
        assert "ml_prediction" in enhancement_data
        assert "comparison" in enhancement_data
        
        # Check project data
        project = enhancement_data["project"]
        assert "id" in project
        assert project["id"] == 1
        assert "name" in project
        
        # Check ML prediction
        ml_pred = enhancement_data["ml_prediction"]
        assert "predicted_co2_tons_year" in ml_pred
        assert ml_pred["predicted_co2_tons_year"] >= 0
        
        # Check comparison
        comparison = enhancement_data["comparison"]
        assert "original_estimate" in comparison
        assert "ml_prediction" in comparison
        assert "difference_percent" in comparison
    
    def test_batch_prediction_limits(self):
        """Test batch prediction with size limits"""
        # Test with small batch
        small_batch = [
            {"area_hectares": 100, "climate_zone": "temperate"},
            {"area_hectares": 200, "climate_zone": "tropical"}
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/batch-predict",
            json=small_batch,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        batch_data = response.json()
        assert batch_data["success"] == True
        assert "results" in batch_data
        
        # Test with oversized batch (should fail)
        oversized_batch = [{"area_hectares": i} for i in range(101)]  # 101 projects
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/batch-predict",
            json=oversized_batch,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400  # Should reject oversized batch
    
    def test_prediction_consistency(self):
        """Test that predictions are consistent for same input"""
        test_project = {
            "area_hectares": 500,
            "climate_zone": "temperate",
            "vegetation_type": "grassland",
            "methodology": "soil_carbon"
        }
        
        # Make multiple requests with same data
        predictions = []
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/v1/ml/predict-co2",
                json=test_project,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            pred_data = response.json()
            predictions.append(pred_data["prediction"]["predicted_co2_tons_year"])
        
        # All predictions should be identical (deterministic models)
        assert all(abs(p - predictions[0]) < 0.001 for p in predictions)
    
    def test_feature_validation(self):
        """Test that feature engineering handles various inputs correctly"""
        # Test with different climate zones
        climate_zones = ["tropical", "temperate", "boreal", "arctic", "mediterranean"]
        
        for climate in climate_zones:
            test_project = {
                "area_hectares": 1000,
                "climate_zone": climate
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/ml/predict-co2",
                json=test_project,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            pred_data = response.json()
            assert pred_data["success"] == True
            
            # Prediction should be reasonable (not zero, not extreme)
            prediction = pred_data["prediction"]["predicted_co2_tons_year"]
            assert 0 < prediction < 100000  # Reasonable range


def run_manual_tests():
    """Run manual tests to validate ML system"""
    print("🧪 Ejecutando pruebas manuales del sistema ML...")
    
    # Test 1: Verificar que el servidor está respondiendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Test 1 - Salud del servidor: {response.status_code}")
        health_data = response.json()
        ml_status = health_data.get("services", {}).get("ml_models")
        print(f"   Estado ML: {ml_status}")
    except Exception as e:
        print(f"❌ Test 1 - Error: {e}")
        return False
    
    # Test 2: Estado de modelos ML
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ml/model-status", timeout=10)
        print(f"✅ Test 2 - Estado de modelos: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            models = status_data.get("ml_models", {}).get("models", [])
            print(f"   Modelos disponibles: {len(models)}")
            metrics = status_data.get("ml_models", {}).get("metrics", {})
            for model, metric in metrics.items():
                r2 = metric.get("r2", 0)
                print(f"   - {model}: R² = {r2:.3f}")
    except Exception as e:
        print(f"❌ Test 2 - Error: {e}")
        return False
    
    # Test 3: Predicción básica
    try:
        test_project = {
            "area_hectares": 1500,
            "climate_zone": "tropical",
            "vegetation_type": "forest",
            "methodology": "reforestation"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ml/predict-co2",
            json=test_project,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"✅ Test 3 - Predicción básica: {response.status_code}")
        if response.status_code == 200:
            pred_data = response.json()
            prediction = pred_data.get("prediction", {}).get("predicted_co2_tons_year", 0)
            print(f"   Predicción para 1500ha: {prediction:.2f} tons CO2/año")
            print(f"   Equivale a: {prediction/1500:.2f} tons CO2/ha/año")
    except Exception as e:
        print(f"❌ Test 3 - Error: {e}")
        return False
    
    # Test 4: Mejora de proyecto existente
    try:
        response = requests.post(f"{BASE_URL}/api/v1/ml/enhance-project/1", timeout=15)
        print(f"✅ Test 4 - Mejora de proyecto: {response.status_code}")
        if response.status_code == 200:
            enhancement_data = response.json()
            original = enhancement_data.get("comparison", {}).get("original_estimate", 0)
            ml_pred = enhancement_data.get("comparison", {}).get("ml_prediction", 0)
            diff_pct = enhancement_data.get("comparison", {}).get("difference_percent", 0)
            print(f"   Original: {original:.0f} tons CO2/año")
            print(f"   ML Predicción: {ml_pred:.0f} tons CO2/año")
            print(f"   Diferencia: {diff_pct:.1f}%")
    except Exception as e:
        print(f"❌ Test 4 - Error: {e}")
        return False
    
    # Test 5: Validación de diferentes escenarios
    test_scenarios = [
        {"area_hectares": 100, "vegetation_type": "grassland", "desc": "Pequeño pastizal"},
        {"area_hectares": 5000, "vegetation_type": "forest", "climate_zone": "tropical", "desc": "Bosque tropical grande"},
        {"area_hectares": 1000, "methodology": "biochar", "desc": "Proyecto biochar"},
        {"area_hectares": 2000, "climate_zone": "arctic", "desc": "Proyecto ártico"},
    ]
    
    print("✅ Test 5 - Escenarios diversos:")
    for i, scenario in enumerate(test_scenarios):
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ml/predict-co2",
                json=scenario,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                pred_data = response.json()
                prediction = pred_data.get("prediction", {}).get("predicted_co2_tons_year", 0)
                area = scenario["area_hectares"]
                per_ha = prediction / area if area > 0 else 0
                print(f"   {i+1}. {scenario['desc']}: {prediction:.0f} tons/año ({per_ha:.1f} tons/ha/año)")
            else:
                print(f"   {i+1}. {scenario['desc']}: Error {response.status_code}")
        except Exception as e:
            print(f"   {i+1}. {scenario['desc']}: Error - {e}")
    
    print("🎉 Todas las pruebas manuales completadas!")
    return True


if __name__ == "__main__":
    run_manual_tests()