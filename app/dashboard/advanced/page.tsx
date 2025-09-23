import { Suspense } from 'react';
import ConnectedInteractiveMap from '@/app/ui/dashboard/advanced/ConnectedInteractiveMap';
import ConnectedCarbonMetrics from '@/app/ui/dashboard/advanced/ConnectedCarbonMetrics';
import RealTimeAnalytics from '@/app/ui/dashboard/advanced/RealTimeAnalytics';

export const dynamic = 'force-dynamic';

export default async function AdvancedDashboardPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-mint-1 via-white to-emerald-1 dark:from-zinc-950 dark:via-zinc-900 dark:to-emerald-950">
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-mint-6 to-emerald-6 bg-clip-text text-transparent mb-2">
            🌍 Nuwa Advanced Carbon Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Real-time monitoring and analytics for global carbon capture projects
          </p>
        </div>

        {/* Real-Time Analytics Section */}
        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Live Monitoring
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Real-time data from satellite networks and ground sensors
            </p>
          </div>
          <Suspense fallback={
            <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 text-center border border-mint-5 dark:border-mint-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-mint-6 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading real-time analytics...</p>
            </div>
          }>
            <RealTimeAnalytics />
          </Suspense>
        </section>

        {/* Interactive Map Section */}
        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Project Locations
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Interactive visualization of carbon capture projects worldwide
            </p>
          </div>
          <Suspense fallback={
            <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 text-center border border-mint-5 dark:border-mint-8">
              <div className="animate-pulse">
                <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mx-auto"></div>
                </div>
              </div>
            </div>
          }>
            <ConnectedInteractiveMap />
          </Suspense>
        </section>

        {/* Carbon Metrics Section */}
        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Carbon Analytics
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Comprehensive analysis and trends of carbon capture performance
            </p>
          </div>
          <Suspense fallback={
            <div className="space-y-4">
              {/* Metrics cards skeleton */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-1"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                    </div>
                  </div>
                ))}
              </div>
              {/* Charts skeleton */}
              <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl shadow-lg border border-mint-5 dark:border-mint-8">
                <div className="animate-pulse">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
                  <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
              </div>
            </div>
          }>
            <ConnectedCarbonMetrics />
          </Suspense>
        </section>

        {/* Footer */}
        <footer className="text-center py-8 border-t border-gray-200 dark:border-gray-700">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              🌱 Powered by PostgreSQL + PostGIS
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Enterprise-grade geospatial database with real-time satellite integration
            </p>
          </div>
          <div className="flex justify-center items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>PostgreSQL + PostGIS Active</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span>ML Models Online</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
              <span>Satellite Network Connected</span>
            </div>
          </div>
        </footer>
      </div>
    </main>
  );
}