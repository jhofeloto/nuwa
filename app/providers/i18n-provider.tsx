'use client';

import { ReactNode, useEffect } from 'react';
import i18next from '@/app/providers/i18n';
import { I18nextProvider } from 'react-i18next';
import { usePathname } from 'next/navigation';

// Extract language from pathname if available
function getLanguageFromPathname(pathname: string): string | null {
  // Check if the pathname starts with a language code
  const pathParts = pathname.split('/');
  if (pathParts.length > 1 && ['en', 'es'].includes(pathParts[1])) {
    return pathParts[1];
  }
  return null;
}

export default function I18nProviderWrapper({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  
  // Ensure i18next uses the correct language from the URL
  useEffect(() => {
    const pathnameLanguage = getLanguageFromPathname(pathname);
    if (pathnameLanguage && i18next.language !== pathnameLanguage) {
      i18next.changeLanguage(pathnameLanguage);
    }
  }, [pathname]);

  return (
    <I18nextProvider i18n={i18next}>
      {children}
    </I18nextProvider>
  );
}