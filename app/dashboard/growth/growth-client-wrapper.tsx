// app/dashboard/growth/client-wrapper.tsx
'use client';

import dynamic from 'next/dynamic';
import { Suspense } from 'react';

const GrowthComponent = dynamic(() => import('@/app/ui/growth/growth-components'), { ssr: false });

export default function GrowthClientWrapper() {
  return (
    <Suspense fallback={
      <div className="w-full h-96 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-mint-9"></div>
      </div>
    }>
      <GrowthComponent />
    </Suspense>
  );
}