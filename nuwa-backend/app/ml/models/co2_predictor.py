"""
CO2 Capture Prediction Models
Main ML models for predicting carbon sequestration
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from ..utils.feature_engineering import CarbonFeatureEngineer, generate_synthetic_training_data


class CO2PredictionModel:
    """
    Main class for CO2 capture prediction using ensemble of ML models.
    """
    
    def __init__(self, model_dir: str = "app/ml/trained_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.feature_engineer = CarbonFeatureEngineer()
        self.scaler = StandardScaler()
        
        # Initialize models
        self.models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'linear_regression': LinearRegression()
        }
        
        self.trained_models = {}
        self.feature_names = self.feature_engineer.get_feature_names()
        self.is_trained = False
        
        # Model performance tracking
        self.model_metrics = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'co2_capture_tons_year') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for training or prediction.
        
        Args:
            df: DataFrame with project data
            target_col: Name of target column
            
        Returns:
            Tuple of (features_df, target_series)
        """
        # Select only the features we need
        X = df[self.feature_names].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Get target if available
        y = df[target_col] if target_col in df.columns else None
        
        return X, y
    
    def train(self, training_data: pd.DataFrame, target_col: str = 'co2_capture_tons_year'):
        """
        Train all models on the provided data.
        
        Args:
            training_data: DataFrame with features and target
            target_col: Name of target column
        """
        self.logger.info("Starting model training...")
        
        # Prepare data
        X, y = self.prepare_data(training_data, target_col)
        
        if y is None:
            raise ValueError(f"Target column '{target_col}' not found in training data")
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train each model
        for model_name, model in self.models.items():
            self.logger.info(f"Training {model_name}...")
            
            # Use scaled features for linear regression, original for tree-based models
            if model_name == 'linear_regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_val_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
            
            # Calculate metrics
            mse = mean_squared_error(y_val, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            
            self.model_metrics[model_name] = {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
            
            self.logger.info(f"{model_name} - RMSE: {rmse:.2f}, R²: {r2:.3f}")
            
            # Store trained model
            self.trained_models[model_name] = model
        
        self.is_trained = True
        
        # Save models
        self.save_models()
        
        self.logger.info("Model training completed!")
    
    def predict(self, project_data: Dict[str, Any], use_ensemble: bool = True) -> Dict[str, Any]:
        """
        Predict CO2 capture for a single project.
        
        Args:
            project_data: Project parameters dictionary
            use_ensemble: Whether to use ensemble prediction
            
        Returns:
            Prediction results with confidence intervals
        """
        if not self.is_trained:
            self.load_models()
        
        # Extract features
        features = self.feature_engineer.extract_features(project_data)
        feature_df = pd.DataFrame([features])
        
        # Prepare data
        X, _ = self.prepare_data(feature_df)
        X_scaled = self.scaler.transform(X)
        
        predictions = {}
        
        # Get predictions from each model
        for model_name, model in self.trained_models.items():
            if model_name == 'linear_regression':
                pred = model.predict(X_scaled)[0]
            else:
                pred = model.predict(X)[0]
            
            predictions[model_name] = max(0, pred)  # Ensure non-negative
        
        if use_ensemble:
            # Weighted ensemble based on R² scores
            weights = {}
            total_r2 = sum(self.model_metrics[name]['r2'] for name in predictions.keys())
            
            for name in predictions.keys():
                weights[name] = self.model_metrics[name]['r2'] / total_r2
            
            ensemble_pred = sum(
                predictions[name] * weights[name] 
                for name in predictions.keys()
            )
            
            # Calculate confidence interval based on model agreement
            pred_values = list(predictions.values())
            std_dev = np.std(pred_values)
            
            result = {
                'predicted_co2_tons_year': ensemble_pred,
                'confidence_interval_lower': max(0, ensemble_pred - 1.96 * std_dev),
                'confidence_interval_upper': ensemble_pred + 1.96 * std_dev,
                'model_agreement_std': std_dev,
                'individual_predictions': predictions,
                'model_weights': weights
            }
        else:
            # Use best performing model (highest R²)
            best_model = max(self.model_metrics.keys(), 
                           key=lambda x: self.model_metrics[x]['r2'])
            
            result = {
                'predicted_co2_tons_year': predictions[best_model],
                'best_model_used': best_model,
                'model_r2_score': self.model_metrics[best_model]['r2'],
                'individual_predictions': predictions
            }
        
        return result
    
    def predict_batch(self, projects: List[Dict[str, Any]], use_ensemble: bool = True) -> List[Dict[str, Any]]:
        """
        Predict CO2 capture for multiple projects.
        
        Args:
            projects: List of project dictionaries
            use_ensemble: Whether to use ensemble prediction
            
        Returns:
            List of prediction results
        """
        results = []
        for project in projects:
            try:
                prediction = self.predict(project, use_ensemble)
                prediction['project_id'] = project.get('id')
                results.append(prediction)
            except Exception as e:
                self.logger.error(f"Error predicting for project {project.get('id')}: {e}")
                results.append({
                    'project_id': project.get('id'),
                    'error': str(e),
                    'predicted_co2_tons_year': 0
                })
        
        return results
    
    def save_models(self):
        """Save trained models and metadata to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save each model
        for model_name, model in self.trained_models.items():
            model_path = self.model_dir / f"{model_name}_{timestamp}.pkl"
            joblib.dump(model, model_path)
        
        # Save scaler
        scaler_path = self.model_dir / f"scaler_{timestamp}.pkl"
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'feature_names': self.feature_names,
            'model_metrics': self.model_metrics,
            'models_saved': list(self.trained_models.keys())
        }
        
        metadata_path = self.model_dir / f"metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update current model symlinks
        for model_name in self.trained_models.keys():
            current_path = self.model_dir / f"{model_name}_current.pkl"
            model_path = self.model_dir / f"{model_name}_{timestamp}.pkl"
            if current_path.exists():
                current_path.unlink()
            current_path.symlink_to(model_path.name)
        
        # Current scaler and metadata
        current_scaler = self.model_dir / "scaler_current.pkl"
        if current_scaler.exists():
            current_scaler.unlink()
        current_scaler.symlink_to(f"scaler_{timestamp}.pkl")
        
        current_metadata = self.model_dir / "metadata_current.json"
        if current_metadata.exists():
            current_metadata.unlink()
        current_metadata.symlink_to(f"metadata_{timestamp}.json")
        
        self.logger.info(f"Models saved with timestamp {timestamp}")
    
    def load_models(self):
        """Load the most recent trained models."""
        try:
            # Load metadata
            metadata_path = self.model_dir / "metadata_current.json"
            if not metadata_path.exists():
                raise FileNotFoundError("No trained models found")
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            self.model_metrics = metadata['model_metrics']
            
            # Load models
            for model_name in metadata['models_saved']:
                model_path = self.model_dir / f"{model_name}_current.pkl"
                self.trained_models[model_name] = joblib.load(model_path)
            
            # Load scaler
            scaler_path = self.model_dir / "scaler_current.pkl"
            self.scaler = joblib.load(scaler_path)
            
            self.is_trained = True
            self.logger.info(f"Models loaded from {metadata['timestamp']}")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models."""
        if not self.is_trained:
            try:
                self.load_models()
            except:
                return {"status": "No trained models available"}
        
        return {
            "status": "trained",
            "models": list(self.trained_models.keys()),
            "metrics": self.model_metrics,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names
        }


class CO2PredictionService:
    """
    Service class for CO2 prediction with automatic model management.
    """
    
    def __init__(self):
        self.model = CO2PredictionModel()
        self.logger = logging.getLogger(__name__)
    
    async def initialize_models(self):
        """Initialize models with synthetic training data if not already trained."""
        try:
            self.model.load_models()
            self.logger.info("Existing trained models loaded successfully")
        except:
            self.logger.info("No existing models found. Training new models with synthetic data...")
            await self.train_with_synthetic_data()
    
    async def train_with_synthetic_data(self, n_samples: int = 5000):
        """Train models using synthetic data."""
        self.logger.info(f"Generating {n_samples} synthetic training samples...")
        training_data = generate_synthetic_training_data(n_samples)
        
        self.logger.info("Training models...")
        self.model.train(training_data)
        
        self.logger.info("Model training completed with synthetic data")
    
    async def predict_co2_capture(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict CO2 capture for a project.
        
        Args:
            project_data: Project parameters
            
        Returns:
            Prediction results
        """
        try:
            if not self.model.is_trained:
                await self.initialize_models()
            
            prediction = self.model.predict(project_data, use_ensemble=True)
            
            # Add additional metadata
            prediction['prediction_timestamp'] = datetime.now().isoformat()
            prediction['model_version'] = 'v1.0'
            
            return prediction
        
        except Exception as e:
            self.logger.error(f"Error in CO2 prediction: {e}")
            return {
                'error': str(e),
                'predicted_co2_tons_year': 0,
                'prediction_timestamp': datetime.now().isoformat()
            }
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and performance metrics."""
        return self.model.get_model_info()


# Global service instance
co2_prediction_service = CO2PredictionService()


if __name__ == "__main__":
    # Test the prediction model
    import asyncio
    
    async def test_model():
        service = CO2PredictionService()
        await service.initialize_models()
        
        # Test prediction
        test_project = {
            'area_hectares': 1000,
            'duration_years': 10,
            'budget_usd': 500000,
            'climate_zone': 'tropical',
            'vegetation_type': 'forest',
            'methodology': 'afforestation',
            'soil_type': 'clay',
            'annual_rainfall_mm': 2000,
            'avg_temperature_c': 25,
            'elevation_m': 500,
            'latitude': -5.5,
            'longitude': -55.0,
            'start_date': '2024-06-01',
            'technology_level': 'high'
        }
        
        prediction = await service.predict_co2_capture(test_project)
        print("Prediction result:", prediction)
        
        model_status = await service.get_model_status()
        print("Model status:", model_status)
    
    asyncio.run(test_model())