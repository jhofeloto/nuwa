'use client';

import React, { useState, useEffect } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveSunburst } from '@nivo/sunburst';
import { motion, AnimatePresence } from 'framer-motion';

interface RealTimeData {
  timestamp: string;
  co2_rate: number;
  active_monitors: number;
  satellite_updates: number;
  ml_predictions: number;
}

interface SatelliteStatus {
  name: string;
  status: 'operational' | 'degraded' | 'offline';
  last_update: string;
  coverage: number;
}

interface RealTimeAnalyticsProps {
  className?: string;
}

export default function RealTimeAnalytics({ className = '' }: RealTimeAnalyticsProps) {
  const [realTimeData, setRealTimeData] = useState<RealTimeData[]>([]);
  const [isLive, setIsLive] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1h' | '6h' | '24h'>('1h');
  const [satellites, setSatellites] = useState<SatelliteStatus[]>([
    { name: 'Sentinel-2', status: 'operational', last_update: '2 min ago', coverage: 98.5 },
    { name: 'Landsat-8', status: 'operational', last_update: '5 min ago', coverage: 87.2 },
    { name: 'Landsat-9', status: 'degraded', last_update: '15 min ago', coverage: 73.8 },
    { name: 'MODIS', status: 'operational', last_update: '1 min ago', coverage: 94.1 }
  ]);

  // Simulate real-time data updates
  useEffect(() => {
    const generateDataPoint = (): RealTimeData => ({
      timestamp: new Date().toISOString(),
      co2_rate: Math.random() * 50 + 100, // 100-150 tons/hour
      active_monitors: Math.floor(Math.random() * 10) + 45, // 45-55 monitors
      satellite_updates: Math.floor(Math.random() * 5) + 15, // 15-20 updates
      ml_predictions: Math.floor(Math.random() * 8) + 25 // 25-33 predictions
    });

    // Initialize with some data points
    const initialData = Array.from({ length: 20 }, (_, i) => {
      const date = new Date();
      date.setMinutes(date.getMinutes() - (19 - i));
      return {
        ...generateDataPoint(),
        timestamp: date.toISOString()
      };
    });

    setRealTimeData(initialData);

    // Update data every 30 seconds if live
    const interval = setInterval(() => {
      if (isLive) {
        setRealTimeData(prev => {
          const newData = [...prev.slice(1), generateDataPoint()];
          return newData;
        });

        // Randomly update satellite status
        if (Math.random() < 0.1) {
          setSatellites(prev => prev.map(sat => ({
            ...sat,
            coverage: Math.max(60, Math.min(100, sat.coverage + (Math.random() - 0.5) * 10)),
            last_update: Math.random() < 0.3 ? 
              `${Math.floor(Math.random() * 10) + 1} min ago` : 
              sat.last_update
          })));
        }
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isLive]);

  // Prepare chart data
  const chartData = [
    {
      id: 'CO₂ Rate',
      color: '#22c55e',
      data: realTimeData.map((d, i) => ({
        x: i,
        y: d.co2_rate
      }))
    },
    {
      id: 'Active Monitors',
      color: '#3b82f6',
      data: realTimeData.map((d, i) => ({
        x: i,
        y: d.active_monitors
      }))
    }
  ];

  // Prepare sunburst data for system overview
  const systemData = {
    name: 'Nuwa System',
    children: [
      {
        name: 'Monitoring',
        children: [
          { name: 'Satellite', value: 35 },
          { name: 'Ground Sensors', value: 28 },
          { name: 'Drones', value: 15 }
        ]
      },
      {
        name: 'Processing',
        children: [
          { name: 'ML Models', value: 42 },
          { name: 'Data Analysis', value: 31 },
          { name: 'Validation', value: 18 }
        ]
      },
      {
        name: 'Reporting',
        children: [
          { name: 'Real-time', value: 25 },
          { name: 'Weekly', value: 20 },
          { name: 'Monthly', value: 15 }
        ]
      }
    ]
  };

  const currentData = realTimeData[realTimeData.length - 1];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Live Status Header */}
      <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              🔴 Real-Time Carbon Monitoring
            </h2>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setIsLive(!isLive)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                isLive 
                  ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300' 
                  : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-300'
              }`}
            >
              {isLive ? 'Stop Live' : 'Start Live'}
            </button>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value as '1h' | '6h' | '24h')}
              className="px-3 py-2 border border-gray-300 rounded-lg bg-white dark:bg-zinc-800 dark:border-gray-600 text-sm"
            >
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
            </select>
          </div>
        </div>
      </div>

      {/* Real-time Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          key={currentData?.co2_rate}
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 0.5 }}
          className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-6 rounded-xl shadow-lg border border-green-200 dark:border-green-800"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 dark:text-green-400">CO₂ Capture Rate</p>
              <p className="text-3xl font-bold text-green-800 dark:text-green-200">
                {currentData?.co2_rate.toFixed(1)}
              </p>
              <p className="text-xs text-green-600 dark:text-green-400">tons/hour</p>
            </div>
            <div className="text-4xl">🌱</div>
          </div>
        </motion.div>

        <motion.div
          key={currentData?.active_monitors}
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 0.5 }}
          className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 p-6 rounded-xl shadow-lg border border-blue-200 dark:border-blue-800"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Active Monitors</p>
              <p className="text-3xl font-bold text-blue-800 dark:text-blue-200">
                {currentData?.active_monitors}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400">sensors online</p>
            </div>
            <div className="text-4xl">📡</div>
          </div>
        </motion.div>

        <motion.div
          key={currentData?.satellite_updates}
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 0.5 }}
          className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 p-6 rounded-xl shadow-lg border border-purple-200 dark:border-purple-800"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Satellite Updates</p>
              <p className="text-3xl font-bold text-purple-800 dark:text-purple-200">
                {currentData?.satellite_updates}
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400">last hour</p>
            </div>
            <div className="text-4xl">🛰️</div>
          </div>
        </motion.div>

        <motion.div
          key={currentData?.ml_predictions}
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 0.5 }}
          className="bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 p-6 rounded-xl shadow-lg border border-orange-200 dark:border-orange-800"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600 dark:text-orange-400">ML Predictions</p>
              <p className="text-3xl font-bold text-orange-800 dark:text-orange-200">
                {currentData?.ml_predictions}
              </p>
              <p className="text-xs text-orange-600 dark:text-orange-400">models running</p>
            </div>
            <div className="text-4xl">🧠</div>
          </div>
        </motion.div>
      </div>

      {/* Real-time Charts */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Live Data Stream */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            📈 Live Data Stream
          </h3>
          <div className="h-64">
            <ResponsiveLine
              data={chartData}
              margin={{ top: 20, right: 110, bottom: 50, left: 60 }}
              xScale={{ type: 'linear', min: 0, max: 19 }}
              yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
              curve="cardinal"
              axisTop={null}
              axisRight={null}
              axisBottom={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Time (last 20 updates)',
                legendOffset: 36,
                legendPosition: 'middle'
              }}
              axisLeft={{
                tickSize: 5,
                tickPadding: 5,
                tickRotation: 0,
                legend: 'Value',
                legendOffset: -40,
                legendPosition: 'middle'
              }}
              pointSize={6}
              pointColor={{ theme: 'background' }}
              pointBorderWidth={2}
              pointBorderColor={{ from: 'serieColor' }}
              useMesh={true}
              animate={true}
              motionConfig="gentle"
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
                  symbolShape: 'circle'
                }
              ]}
            />
          </div>
        </div>

        {/* System Overview */}
        <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            ⚙️ System Overview
          </h3>
          <div className="h-64">
            <ResponsiveSunburst
              data={systemData}
              margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
              identity="name"
              value="value"
              cornerRadius={2}
              borderWidth={1}
              borderColor={'white'}
              colors={{ scheme: 'set3' }}
              childColor={{
                from: 'color',
                modifiers: [
                  ['brighter', 0.1]
                ]
              }}
              animate={true}
              motionConfig="gentle"
            />
          </div>
        </div>
      </div>

      {/* Satellite Status */}
      <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          🛰️ Satellite Network Status
        </h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {satellites.map((satellite, index) => (
            <motion.div
              key={satellite.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-2 ${
                satellite.status === 'operational'
                  ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                  : satellite.status === 'degraded'
                  ? 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20'
                  : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900 dark:text-white">
                  {satellite.name}
                </span>
                <div
                  className={`w-3 h-3 rounded-full ${
                    satellite.status === 'operational'
                      ? 'bg-green-500'
                      : satellite.status === 'degraded'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                ></div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Coverage: {satellite.coverage.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Updated: {satellite.last_update}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}