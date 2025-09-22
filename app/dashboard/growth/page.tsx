// app/dashboard/growth/page.tsx
import { Suspense } from 'react';
import GrowthClientWrapper from './growth-client-wrapper';

export default function Growth() {
  return (
    <main className="min-h-screen w-full">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-6 md:py-12">
        <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl shadow-md border border-mint-5 dark:border-mint-8">
          <div className="p-4 md:p-6 lg:p-8">
            <Suspense fallback={
              <div className="w-full h-96 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-mint-9"></div>
              </div>
            }>
              <GrowthClientWrapper />
            </Suspense>
          </div>
        </div>
      </div>
    </main>
  );
}