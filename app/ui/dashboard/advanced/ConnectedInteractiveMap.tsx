'use client';

import React from 'react';
import InteractiveMap from './InteractiveMap';
import { useRealTimeData } from '@/app/lib/hooks/useRealTimeData';

interface ConnectedInteractiveMapProps {
  className?: string;
}

export default function ConnectedInteractiveMap({ className = '' }: ConnectedInteractiveMapProps) {
  const { projects, isLoading, error } = useRealTimeData();

  if (isLoading) {
    return (
      <div className={`bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 text-center border border-mint-5 dark:border-mint-8 ${className}`}>
        <div className="animate-pulse">
          <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 text-center border border-red-200 dark:border-red-800 ${className}`}>
        <div className="text-red-600 dark:text-red-400 mb-4">
          <svg className="w-12 h-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold mb-2">Connection Error</h3>
          <p className="text-sm">Unable to load project data. Using offline mode with sample data.</p>
        </div>
        {/* Fallback to default InteractiveMap with sample data */}
        <InteractiveMap 
          className=""
          projects={[
            {
              id: 1,
              name: "Costa Rica Reforestation (Sample)",
              latitude: 10.5,
              longitude: -84.2,
              co2_estimated: 15420,
              status: "ACTIVE",
              project_type: "REFORESTATION"
            },
            {
              id: 2,
              name: "Amazon Conservation Brazil (Sample)",
              latitude: -3.4,
              longitude: -62.1,
              co2_estimated: 89750,
              status: "ACTIVE", 
              project_type: "FOREST_MANAGEMENT"
            },
            {
              id: 3,
              name: "Kenya Afforestation Program (Sample)",
              latitude: -1.3,
              longitude: 36.8,
              co2_estimated: 23680,
              status: "ACTIVE",
              project_type: "AFFORESTATION"
            }
          ]}
        />
      </div>
    );
  }

  // Transform project data to match InteractiveMap interface
  const mapProjects = projects.map(project => ({
    id: project.id,
    name: project.name,
    latitude: project.latitude || 0,
    longitude: project.longitude || 0,
    co2_estimated: project.estimated_co2_capture_tons_year || 0,
    status: project.status,
    project_type: project.project_type,
  }));

  return (
    <InteractiveMap 
      className={className}
      projects={mapProjects}
    />
  );
}