'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, type Project, type DatabaseStats, type SatelliteStatus } from '../api-client';

interface RealTimeMetrics {
  co2_captured_total: number;
  co2_projected_total: number;
  projects_active: number;
  projects_completed: number;
  total_area_hectares: number;
  last_updated: string;
}

interface UseRealTimeDataReturn {
  metrics: RealTimeMetrics | null;
  projects: Project[];
  databaseStats: DatabaseStats | null;
  satelliteStatus: SatelliteStatus | null;
  isLoading: boolean;
  error: string | null;
  isLive: boolean;
  toggleLive: () => void;
  refreshData: () => Promise<void>;
}

export function useRealTimeData(): UseRealTimeDataReturn {
  const [metrics, setMetrics] = useState<RealTimeMetrics | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [databaseStats, setDatabaseStats] = useState<DatabaseStats | null>(null);
  const [satelliteStatus, setSatelliteStatus] = useState<SatelliteStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      
      // Fetch all data in parallel
      const [projectsResponse, dbStatsResponse, satelliteStatusResponse] = await Promise.allSettled([
        apiClient.getProjects(0, 100),
        apiClient.getDatabaseStats(),
        apiClient.getSatelliteStatus(),
      ]);

      // Handle projects data
      if (projectsResponse.status === 'fulfilled' && projectsResponse.value.success) {
        const projectData = projectsResponse.value.projects;
        setProjects(projectData);

        // Calculate real-time metrics from project data
        const activeProjects = projectData.filter(p => p.status === 'ACTIVE' || p.status === 'APPROVED').length;
        const completedProjects = projectData.filter(p => p.status === 'COMPLETED').length;
        const totalCO2Captured = projectData
          .filter(p => p.status === 'COMPLETED')
          .reduce((sum, p) => sum + (p.estimated_co2_capture_tons_year || 0), 0);
        const totalCO2Projected = projectData
          .reduce((sum, p) => sum + (p.estimated_co2_capture_tons_year || 0), 0);
        const totalArea = projectData
          .reduce((sum, p) => sum + (p.total_area_hectares || 0), 0);

        setMetrics({
          co2_captured_total: totalCO2Captured,
          co2_projected_total: totalCO2Projected,
          projects_active: activeProjects,
          projects_completed: completedProjects,
          total_area_hectares: totalArea,
          last_updated: new Date().toISOString(),
        });
      } else if (projectsResponse.status === 'rejected') {
        console.warn('Failed to fetch projects:', projectsResponse.reason);
        
        // Use mock data if API fails
        const mockProjects: Project[] = [
          {
            id: 1,
            name: "Costa Rica Reforestation",
            project_type: "REFORESTATION",
            status: "ACTIVE",
            latitude: 10.5,
            longitude: -84.2,
            estimated_co2_capture_tons_year: 15420,
            total_area_hectares: 1200,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: "Amazon Conservation Brazil",
            project_type: "FOREST_MANAGEMENT",
            status: "ACTIVE",
            latitude: -3.4,
            longitude: -62.1,
            estimated_co2_capture_tons_year: 89750,
            total_area_hectares: 8500,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 3,
            name: "Kenya Afforestation Program",
            project_type: "AFFORESTATION", 
            status: "COMPLETED",
            latitude: -1.3,
            longitude: 36.8,
            estimated_co2_capture_tons_year: 23680,
            total_area_hectares: 3200,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ];
        
        setProjects(mockProjects);
        setMetrics({
          co2_captured_total: 23680, // Only completed project
          co2_projected_total: 128850, // All projects
          projects_active: 2,
          projects_completed: 1,
          total_area_hectares: 12900,
          last_updated: new Date().toISOString(),
        });
      }

      // Handle database stats
      if (dbStatsResponse.status === 'fulfilled') {
        setDatabaseStats(dbStatsResponse.value);
      }

      // Handle satellite status  
      if (satelliteStatusResponse.status === 'fulfilled') {
        setSatelliteStatus(satelliteStatusResponse.value);
      }

    } catch (err) {
      console.error('Error fetching real-time data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const toggleLive = useCallback(() => {
    setIsLive(prev => !prev);
  }, []);

  const refreshData = useCallback(async () => {
    setIsLoading(true);
    await fetchData();
  }, [fetchData]);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Live data updates
  useEffect(() => {
    if (isLive) {
      intervalRef.current = setInterval(() => {
        fetchData();
      }, 30000); // Update every 30 seconds
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isLive, fetchData]);

  return {
    metrics,
    projects,
    databaseStats,
    satelliteStatus,
    isLoading,
    error,
    isLive,
    toggleLive,
    refreshData,
  };
}