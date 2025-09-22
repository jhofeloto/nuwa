import CardWrapper from '@/app/ui/dashboard/cards';
import ProjectComponent from '@/app/ui/dashboard/projects/project-component';
import SimulateComponent from '@/app/ui/dashboard/projects/simulate/simulate-component';
import { Suspense } from 'react';

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <main className="min-h-screen">
      <div className="flex-grow md:overflow-y-auto md:p-12">
        <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl shadow-md p-6 mb-8 border border-mint-5 dark:border-mint-8">
          <Suspense fallback={<div>Loading...</div>}>
            <CardWrapper projectId={id} />
          </Suspense>
        </div>
        <div className="mt-6">
          <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl border border-mint-5 dark:border-mint-8 shadow-md overflow-hidden">
            <Suspense fallback={<div>Loading...</div>}>
              <ProjectComponent projectId={id} />
            </Suspense>
          </div>
        </div>
        <div className="mt-6">
        <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl border border-mint-5 dark:border-mint-8 shadow-md overflow-hidden">
          <Suspense fallback={<div>Loading...</div>}>
            <SimulateComponent projectId={id} />
          </Suspense>
        </div>
        </div>
      </div>
    </main>
  );
}
