/**
 * API Client for Nuwa PostgreSQL + PostGIS Backend
 * Provides typed methods to interact with the carbon capture platform API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://8001-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev';

export interface Project {
  id: number;
  name: string;
  description?: string;
  project_type: string;
  status: string;
  latitude?: number;
  longitude?: number;
  total_area_hectares?: number;
  project_area_hectares?: number;
  estimated_co2_capture_tons_year?: number;
  country?: string;
  region?: string;
  created_at: string;
  updated_at: string;
}

export interface MLPredictionRequest {
  latitude: number;
  longitude: number;
  temperature: number;
  precipitation: number;
  soil_ph: number;
  elevation: number;
  tree_species: string[];
  area_hectares: number;
}

export interface MLPredictionResponse {
  success: boolean;
  ml_prediction: {
    predicted_co2_tons_year: number;
    confidence_interval_lower: number;
    confidence_interval_upper: number;
    model_agreement_std: number;
    individual_predictions: Record<string, number>;
    model_weights: Record<string, number>;
    prediction_timestamp: string;
    model_version: string;
  };
  input_features: MLPredictionRequest;
  timestamp: string;
}

export interface SatelliteAnalysisRequest {
  bounds: [number, number, number, number]; // [min_lon, min_lat, max_lon, max_lat]
  project_start_date: string;
  analysis_date?: string;
}

export interface SatelliteAnalysisResponse {
  success: boolean;
  satellite_analysis: {
    success: boolean;
    project_bounds: number[];
    analysis_period: {
      project_start: string;
      analysis_date: string;
      monitoring_duration_days: number;
    };
    satellite_analysis: {
      data_source: string;
      area_analysis: {
        total_area_hectares: number;
        bounds: number[];
        changed_area_hectares: number;
        change_percentage: number;
        stable_area_hectares: number;
      };
      vegetation_monitoring: {
        monitoring_available: boolean;
        baseline_ndvi: number;
        current_ndvi: number;
        ndvi_change: number;
        vegetation_trend: string;
        baseline_health: string;
        current_health: string;
        confidence: string;
      };
      change_detection: {
        change_detection_available: boolean;
        primary_change_type: string;
        confidence_score: number;
        change_significance: string;
        environmental_impact: Record<string, any>;
        analysis_quality: {
          temporal_consistency: number;
          spatial_accuracy: number;
          overall_confidence: number;
          detection_threshold: string;
        };
      };
      carbon_impact_assessment: {
        assessment_available: boolean;
        estimated_biomass_tons_ha: number;
        forest_coverage_percent: number;
        carbon_sequestration_potential: string;
      };
    };
  };
  timestamp: string;
}

export interface GeospatialQueryRequest {
  query_type: string;
  latitude: number;
  longitude: number;
  radius_km: number;
}

export interface DatabaseStats {
  success: boolean;
  database_statistics: {
    total_projects: number;
    total_geospatial_datasets: number;
    projects_by_type: Record<string, number>;
    total_project_area_hectares: number;
    projects_by_country: Record<string, number>;
  };
  postgis_features: boolean;
  timestamp: string;
}

export interface SatelliteStatus {
  success: boolean;
  satellite_services: {
    status: string;
    available_clients: string[];
    default_client: string;
    supported_satellites: Record<string, any>;
    analysis_capabilities: string[];
  };
  system_status: {
    satellite_initialized: boolean;
    services_available: boolean;
  };
  timestamp: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // System endpoints
  async getHealthCheck() {
    return this.request<{
      status: string;
      timestamp: string;
      uptime_seconds: number;
      database: any;
      postgis: any;
      services: any;
      features: any;
    }>('/health');
  }

  // Project endpoints
  async getProjects(skip: number = 0, limit: number = 100) {
    return this.request<{
      success: boolean;
      projects: Project[];
      total_count: number;
      page_info: {
        skip: number;
        limit: number;
        has_next: boolean;
      };
    }>(`/api/v1/projects?skip=${skip}&limit=${limit}`);
  }

  async getProject(id: number) {
    return this.request<{
      success: boolean;
      project: Project;
    }>(`/api/v1/projects/${id}`);
  }

  async createProject(projectData: Partial<Project>) {
    return this.request<{
      success: boolean;
      project: Project;
    }>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  // ML endpoints
  async predictCO2(request: MLPredictionRequest): Promise<MLPredictionResponse> {
    return this.request<MLPredictionResponse>('/api/v1/ml/predict-co2', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Satellite endpoints
  async analyzeSatelliteData(request: SatelliteAnalysisRequest): Promise<SatelliteAnalysisResponse> {
    return this.request<SatelliteAnalysisResponse>('/api/v1/satellite/analyze-project', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getSatelliteStatus(): Promise<SatelliteStatus> {
    return this.request<SatelliteStatus>('/api/v1/satellite/status');
  }

  // Geospatial endpoints
  async performGeospatialQuery(request: GeospatialQueryRequest) {
    return this.request('/api/v1/geospatial/spatial-query', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Analytics endpoints
  async getDatabaseStats(): Promise<DatabaseStats> {
    return this.request<DatabaseStats>('/api/v1/analytics/database-stats');
  }

  // Utility methods for common use cases
  async getProjectsNearLocation(latitude: number, longitude: number, radiusKm: number = 50) {
    try {
      const query: GeospatialQueryRequest = {
        query_type: 'projects_near_point',
        latitude,
        longitude,
        radius_km: radiusKm,
      };
      
      return await this.performGeospatialQuery(query);
    } catch (error) {
      console.warn('Geospatial query failed, falling back to basic project list');
      return await this.getProjects();
    }
  }

  async getProjectAnalytics() {
    try {
      const [projects, dbStats, satelliteStatus] = await Promise.allSettled([
        this.getProjects(0, 1000), // Get more projects for analytics
        this.getDatabaseStats(),
        this.getSatelliteStatus(),
      ]);

      return {
        projects: projects.status === 'fulfilled' ? projects.value : null,
        database: dbStats.status === 'fulfilled' ? dbStats.value : null,
        satellite: satelliteStatus.status === 'fulfilled' ? satelliteStatus.value : null,
      };
    } catch (error) {
      console.error('Failed to get project analytics:', error);
      throw error;
    }
  }

  async simulateCO2Prediction(latitude: number, longitude: number): Promise<MLPredictionResponse> {
    // Default parameters for simulation
    const request: MLPredictionRequest = {
      latitude,
      longitude,
      temperature: 25.0 + (Math.random() - 0.5) * 10, // 20-30°C
      precipitation: 2000 + Math.random() * 1000, // 2000-3000mm
      soil_ph: 6.0 + Math.random() * 2, // 6.0-8.0
      elevation: Math.random() * 1000, // 0-1000m
      tree_species: ['Generic Forest Species'],
      area_hectares: 100 + Math.random() * 400, // 100-500 hectares
    };

    return this.predictCO2(request);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export hook for React components
export function useApiClient() {
  return apiClient;
}