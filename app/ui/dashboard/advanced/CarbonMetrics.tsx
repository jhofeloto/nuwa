'use client';

import React, { useState, useEffect } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveBar } from '@nivo/bar';
import { ResponsiveTreeMap } from '@nivo/treemap';
import { ResponsiveCirclePacking } from '@nivo/circle-packing';
import { motion } from 'framer-motion';

interface CarbonData {
  co2_captured: number;
  co2_projected: number;
  projects_active: number;
  projects_completed: number;
  total_area: number;
  monthly_data: Array<{
    month: string;
    captured: number;
    projected: number;
  }>;
  project_types: Array<{
    type: string;
    count: number;
    co2_total: number;
  }>;
}

interface CarbonMetricsProps {
  data?: CarbonData;
  className?: string;
}

// Mock data for demonstration
const mockData: CarbonData = {
  co2_captured: 125340,
  co2_projected: 890250,
  projects_active: 47,
  projects_completed: 23,
  total_area: 15680,
  monthly_data: [
    { month: 'Jan', captured: 8500, projected: 12000 },
    { month: 'Feb', captured: 9200, projected: 13500 },
    { month: 'Mar', captured: 10100, projected: 15000 },
    { month: 'Apr', captured: 11800, projected: 16800 },
    { month: 'May', captured: 13200, projected: 18500 },
    { month: 'Jun', captured: 15100, projected: 20200 },
    { month: 'Jul', captured: 16800, projected: 22100 },
    { month: 'Aug', captured: 18500, projected: 24000 },
    { month: 'Sep', captured: 20200, projected: 26300 },
    { month: 'Oct', captured: 22100, projected: 28800 },
    { month: 'Nov', captured: 24000, projected: 31500 },
    { month: 'Dec', captured: 26300, projected: 34200 }
  ],
  project_types: [
    { type: 'Reforestation', count: 18, co2_total: 345000 },
    { type: 'Afforestation', count: 12, co2_total: 256000 },
    { type: 'Forest Management', count: 9, co2_total: 178000 },
    { type: 'Agroforestry', count: 8, co2_total: 156000 },
    { type: 'Soil Carbon', count: 6, co2_total: 98000 },
    { type: 'Wetland Restoration', count: 4, co2_total: 67000 },
    { type: 'Direct Air Capture', count: 3, co2_total: 89000 }
  ]
};

export default function CarbonMetrics({ data = mockData, className = '' }: CarbonMetricsProps) {
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y'>('1Y');
  const [selectedMetric, setSelectedMetric] = useState<'captured' | 'projected' | 'both'>('both');

  // Prepare line chart data
  const lineData = [
    {
      id: 'CO₂ Captured',
      color: '#22c55e',
      data: data.monthly_data.map(d => ({
        x: d.month,
        y: d.captured
      }))
    },
    {
      id: 'CO₂ Projected',
      color: '#3b82f6',
      data: data.monthly_data.map(d => ({
        x: d.month,
        y: d.projected
      }))
    }
  ];

  // Prepare bar chart data
  const barData = data.project_types.map(d => ({
    type: d.type,
    count: d.count,
    co2_total: d.co2_total / 1000, // Convert to thousands
    co2TotalColor: '#16a34a',
    countColor: '#3b82f6'
  }));

  // Prepare treemap data
  const treeMapData = {
    name: 'Projects',
    children: data.project_types.map(d => ({
      name: d.type,
      value: d.co2_total,
      count: d.count
    }))
  };

  // Prepare circle packing data
  const circlePackingData = {
    name: 'Carbon Portfolio',
    children: data.project_types.map(d => ({
      name: d.type,
      value: d.co2_total,
      count: d.count
    }))
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">CO₂ Captured</p>
              <p className="text-2xl font-bold text-green-600">{data.co2_captured.toLocaleString()}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">tons this year</p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              🌱
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Projected CO₂</p>
              <p className="text-2xl font-bold text-blue-600">{data.co2_projected.toLocaleString()}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">tons potential</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              📈
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Projects</p>
              <p className="text-2xl font-bold text-mint-6">{data.projects_active}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">{data.projects_completed} completed</p>
            </div>
            <div className="w-12 h-12 bg-mint-100 dark:bg-mint-900/30 rounded-lg flex items-center justify-center">
              🏗️
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Area</p>
              <p className="text-2xl font-bold text-emerald-600">{data.total_area.toLocaleString()}</p>
              <p className="text-xs text-gray-500 dark:text-gray-500">hectares managed</p>
            </div>
            <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
              🌍
            </div>
          </div>
        </motion.div>
      </div>

      {/* CO₂ Trend Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            📊 CO₂ Capture Trends
          </h3>
          <div className="flex gap-2">
            {(['1M', '3M', '6M', '1Y'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-sm rounded-md ${
                  timeRange === range
                    ? 'bg-mint-6 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
        <div className="h-80">
          <ResponsiveLine
            data={lineData}
            margin={{ top: 20, right: 110, bottom: 50, left: 60 }}
            xScale={{ type: 'point' }}
            yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
            yFormat=" >-.2f"
            curve="cardinal"
            axisTop={null}
            axisRight={null}
            axisBottom={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: 'Month',
              legendOffset: 36,
              legendPosition: 'middle'
            }}
            axisLeft={{
              tickSize: 5,
              tickPadding: 5,
              tickRotation: 0,
              legend: 'CO₂ (tons)',
              legendOffset: -40,
              legendPosition: 'middle'
            }}
            pointSize={8}
            pointColor={{ theme: 'background' }}
            pointBorderWidth={2}
            pointBorderColor={{ from: 'serieColor' }}
            pointLabelYOffset={-12}
            useMesh={true}
            legends={[
              {
                anchor: 'bottom-right',
                direction: 'column',
                justify: false,
                translateX: 100,
                translateY: 0,
                itemsSpacing: 0,
                itemDirection: 'left-to-right',
                itemWidth: 80,
                itemHeight: 20,
                itemOpacity: 0.75,
                symbolSize: 12,
                symbolShape: 'circle',
                symbolBorderColor: 'rgba(0, 0, 0, .5)',
                effects: [
                  {
                    on: 'hover',
                    style: {
                      itemBackground: 'rgba(0, 0, 0, .03)',
                      itemOpacity: 1
                    }
                  }
                ]
              }
            ]}
            theme={{
              background: 'transparent',
              text: {
                fill: '#374151',
                fontSize: 11
              },
              axis: {
                domain: {
                  line: {
                    stroke: '#d1d5db',
                    strokeWidth: 1
                  }
                },
                legend: {
                  text: {
                    fill: '#6b7280',
                    fontSize: 12,
                    fontWeight: 600
                  }
                },
                ticks: {
                  line: {
                    stroke: '#d1d5db',
                    strokeWidth: 1
                  },
                  text: {
                    fill: '#6b7280',
                    fontSize: 10
                  }
                }
              },
              grid: {
                line: {
                  stroke: '#f3f4f6',
                  strokeWidth: 1
                }
              }
            }}
          />
        </div>
      </motion.div>

      {/* Project Types Analysis */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Project Types Bar Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            🌳 Projects by Type
          </h3>
          <div className="h-64">
            <ResponsiveBar
              data={barData}
              keys={['count']}
              indexBy="type"
              margin={{ top: 20, right: 60, bottom: 80, left: 60 }}
              padding={0.3}
              valueScale={{ type: 'linear' }}
              indexScale={{ type: 'band', round: true }}
              colors={['#16a34a']}
              borderColor={{
                from: 'color',
                modifiers: [
                  ['darker', 1.6]
                ]
              }}
              axisTop={null}
              axisRight={null}
              axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: -45,
                legend: 'Project Type',
                legendPosition: 'middle',
                legendOffset: 70
              }}
              axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Number of Projects',
                legendPosition: 'middle',
                legendOffset: -40
              }}
              labelSkipWidth={12}
              labelSkipHeight={12}
              labelTextColor={{
                from: 'color',
                modifiers: [
                  ['darker', 1.6]
                ]
              }}
              theme={{
                background: 'transparent',
                text: {
                  fill: '#374151',
                  fontSize: 11
                },
                axis: {
                  domain: {
                    line: {
                      stroke: '#d1d5db',
                      strokeWidth: 1
                    }
                  },
                  legend: {
                    text: {
                      fill: '#6b7280',
                      fontSize: 12,
                      fontWeight: 600
                    }
                  },
                  ticks: {
                    line: {
                      stroke: '#d1d5db',
                      strokeWidth: 1
                    },
                    text: {
                      fill: '#6b7280',
                      fontSize: 10
                    }
                  }
                },
                grid: {
                  line: {
                    stroke: '#f3f4f6',
                    strokeWidth: 1
                  }
                }
              }}
            />
          </div>
        </motion.div>

        {/* CO₂ Impact TreeMap */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            💚 CO₂ Impact Distribution
          </h3>
          <div className="h-64">
            <ResponsiveTreeMap
              data={treeMapData}
              identity="name"
              value="value"
              margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
              labelSkipSize={12}
              labelTextColor={{
                from: 'color',
                modifiers: [
                  ['darker', 1.2]
                ]
              }}
              colors={['#dcfce7', '#bbf7d0', '#86efac', '#4ade80', '#22c55e', '#16a34a', '#15803d']}
              borderColor={{
                from: 'color',
                modifiers: [
                  ['darker', 0.1]
                ]
              }}
              theme={{
                labels: {
                  text: {
                    fill: '#ffffff',
                    fontSize: 10,
                    fontWeight: 'bold'
                  }
                }
              }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  );
}