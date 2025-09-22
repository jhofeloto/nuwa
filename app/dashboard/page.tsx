import CardWrapper from '@/app/ui/dashboard/cards';
import ProjectTable from '@/app/ui/dashboard/projects/page';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';

export default async function Page() {
  return (
    <main className="min-h-screen">
      <div className="flex-grow md:overflow-y-auto md:p-12">
        <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl shadow-md p-6 mb-8 border border-mint-5 dark:border-mint-8">
        <Suspense fallback={<div>Loading...</div>}>
          <CardWrapper />
          </Suspense>
        </div>
        
        <div className="mt-6">
          <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl border border-mint-5 dark:border-mint-8 shadow-md overflow-hidden">
            <Suspense fallback={<div>Loading...</div>}>
              <ProjectTable />
            </Suspense>
          </div>
        </div>
      </div>
    </main>
  );
}