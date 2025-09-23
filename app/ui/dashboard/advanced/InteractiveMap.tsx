'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Project {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  co2_estimated: number;
  status: string;
  project_type: string;
}

interface InteractiveMapProps {
  projects?: Project[];
  className?: string;
}

export default function InteractiveMap({ projects = [], className = '' }: InteractiveMapProps) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [mapCenter, setMapCenter] = useState({ lat: 10.5, lng: -84.2 });
  const [zoom, setZoom] = useState(6);

  // Convert latitude/longitude to SVG coordinates
  const projectToSVG = (lat: number, lng: number) => {
    // Simple projection for demonstration (not geographically accurate)
    const x = ((lng + 180) / 360) * 800;
    const y = ((90 - lat) / 180) * 400;
    return { x, y };
  };

  const projectTypeColors = {
    AFFORESTATION: '#22c55e',
    REFORESTATION: '#16a34a',
    FOREST_MANAGEMENT: '#15803d',
    AGROFORESTRY: '#65a30d',
    GRASSLAND_MANAGEMENT: '#84cc16',
    WETLAND_RESTORATION: '#0ea5e9',
    SOIL_CARBON: '#8b5cf6',
    BIOCHAR: '#a855f7',
    DIRECT_AIR_CAPTURE: '#ec4899',
    BIOMASS_ENERGY: '#f59e0b',
    OTHER: '#6b7280'
  };

  return (
    <div className={`bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
          🌍 Carbon Capture Projects Map
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setZoom(Math.min(zoom + 1, 10))}
            className="px-3 py-1 bg-mint-6 hover:bg-mint-7 text-white rounded-md text-sm"
          >
            Zoom In
          </button>
          <button
            onClick={() => setZoom(Math.max(zoom - 1, 1))}
            className="px-3 py-1 bg-mint-6 hover:bg-mint-7 text-white rounded-md text-sm"
          >
            Zoom Out
          </button>
        </div>
      </div>

      {/* Interactive SVG Map */}
      <div className="relative bg-gradient-to-br from-blue-100 to-green-100 dark:from-blue-900 dark:to-green-900 rounded-lg overflow-hidden">
        <svg
          viewBox="0 0 800 400"
          className="w-full h-80 cursor-move"
          style={{ background: 'linear-gradient(to bottom, #87CEEB 0%, #98FB98 100%)' }}
        >
          {/* World outline (simplified) */}
          <defs>
            <pattern id="waterPattern" patternUnits="userSpaceOnUse" width="4" height="4">
              <rect width="4" height="4" fill="#87CEEB" opacity="0.3"/>
              <circle cx="2" cy="2" r="1" fill="#4682B4" opacity="0.5"/>
            </pattern>
          </defs>

          {/* Ocean background */}
          <rect width="800" height="400" fill="url(#waterPattern)" />

          {/* Continents (simplified shapes) */}
          {/* North America */}
          <path
            d="M 50 80 Q 150 60 250 90 L 280 140 Q 250 180 200 170 L 150 190 Q 100 160 50 140 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* South America */}
          <path
            d="M 180 200 Q 220 190 240 220 L 250 300 Q 230 350 200 340 L 170 320 Q 160 280 170 240 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Europe */}
          <path
            d="M 350 60 Q 420 50 450 80 L 460 120 Q 430 140 400 130 L 370 120 Q 340 90 350 60 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Africa */}
          <path
            d="M 380 130 Q 450 120 480 150 L 490 250 Q 470 320 430 310 L 390 280 Q 370 200 380 130 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Asia */}
          <path
            d="M 460 50 Q 600 40 700 70 L 720 140 Q 680 180 620 170 L 500 160 Q 450 100 460 50 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Australia */}
          <path
            d="M 580 280 Q 650 270 680 290 L 690 320 Q 670 340 640 335 L 590 330 Q 570 300 580 280 Z"
            fill="#90EE90"
            stroke="#228B22"
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Project markers */}
          {projects.map((project, index) => {
            const { x, y } = projectToSVG(project.latitude, project.longitude);
            const color = projectTypeColors[project.project_type as keyof typeof projectTypeColors] || '#6b7280';
            
            return (
              <g key={project.id}>
                <motion.circle
                  cx={x}
                  cy={y}
                  r={Math.max(4, Math.min(project.co2_estimated / 100, 15))}
                  fill={color}
                  stroke="#fff"
                  strokeWidth="2"
                  className="cursor-pointer hover:opacity-80"
                  onClick={() => setSelectedProject(project)}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.2 }}
                />
                <motion.circle
                  cx={x}
                  cy={y}
                  r={Math.max(6, Math.min(project.co2_estimated / 80, 20))}
                  fill="none"
                  stroke={color}
                  strokeWidth="1"
                  opacity="0.3"
                  initial={{ scale: 0 }}
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ 
                    repeat: Infinity, 
                    duration: 2,
                    delay: index * 0.1 
                  }}
                />
              </g>
            );
          })}
        </svg>

        {/* Project details tooltip */}
        {selectedProject && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-4 right-4 bg-white dark:bg-zinc-800 p-4 rounded-lg shadow-lg max-w-xs"
          >
            <button
              onClick={() => setSelectedProject(null)}
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
            <h4 className="font-bold text-gray-900 dark:text-white mb-2">
              {selectedProject.name}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <span className="font-medium">Type:</span> {selectedProject.project_type.replace(/_/g, ' ')}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <span className="font-medium">Status:</span> {selectedProject.status}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <span className="font-medium">CO₂ Potential:</span> {selectedProject.co2_estimated.toLocaleString()} tons/year
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              <span className="font-medium">Location:</span> {selectedProject.latitude.toFixed(2)}°, {selectedProject.longitude.toFixed(2)}°
            </p>
          </motion.div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 p-3 bg-gray-50 dark:bg-zinc-800 rounded-lg">
        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Project Types</h4>
        <div className="flex flex-wrap gap-3">
          {Object.entries(projectTypeColors).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1 text-sm">
              <div 
                className="w-3 h-3 rounded-full border border-gray-300"
                style={{ backgroundColor: color }}
              />
              <span className="text-gray-700 dark:text-gray-300">
                {type.replace(/_/g, ' ')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Map stats */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="bg-gray-50 dark:bg-zinc-800 p-3 rounded-lg">
          <div className="text-2xl font-bold text-mint-6">{projects.length}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Active Projects</div>
        </div>
        <div className="bg-gray-50 dark:bg-zinc-800 p-3 rounded-lg">
          <div className="text-2xl font-bold text-mint-6">
            {projects.reduce((sum, p) => sum + p.co2_estimated, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total CO₂ Tons/Year</div>
        </div>
        <div className="bg-gray-50 dark:bg-zinc-800 p-3 rounded-lg">
          <div className="text-2xl font-bold text-mint-6">
            {new Set(projects.map(p => p.project_type)).size}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Project Types</div>
        </div>
      </div>
    </div>
  );
}