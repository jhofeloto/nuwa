'use client';

import { ReactNode } from 'react';
import dynamic from 'next/dynamic';

const I18nProvider = dynamic(() => import('./i18n-provider'), {
  ssr: false
});

export default function I18nProviderClientWrapper({ children }: { children: ReactNode }) {
  return <I18nProvider>{children}</I18nProvider>;
}