'use client';
import { useEffect } from 'react';
import i18next from 'i18next';
import { initReactI18next, useTranslation } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import { usePathname, useRouter } from 'next/navigation';

// Initialize i18next once
if (!i18next.isInitialized) {
  i18next
    .use(HttpBackend) // Load translations from /public/locales
    .use(LanguageDetector) // Detect browser language
    .use(initReactI18next)
    .init({
      fallbackLng: 'en',
      supportedLngs: ['en', 'es'],
      // debug: process.env.NODE_ENV === 'development',
      detection: {
        order: ['path', 'cookie', 'localStorage', 'navigator'],
        caches: ['cookie'],
        lookupFromPathIndex: 0,
      },
      backend: {
        loadPath: '/locales/{{lng}}/{{ns}}.json',
      },
      ns: ['common'],
      defaultNS: 'common',
      react: { useSuspense: false },
    });
}

// Custom hook to handle language changes with Next.js navigation
export function useI18nRouter() {
  const router = useRouter();
  const pathname = usePathname();
  const { i18n } = useTranslation();

  useEffect(() => {
    const handleLanguageChange = (lng) => {
      // Only navigate if we need to change the URL
      const currentLang = pathname.split('/')[1];
      if (currentLang !== lng && (currentLang === 'en' || currentLang === 'es')) {
        // Replace the language prefix in the URL
        const newPath = pathname.replace(`/${currentLang}`, `/${lng}`);
        router.push(newPath);
      } else if (!(currentLang === 'en' || currentLang === 'es')) {
        // If no language prefix, add it
        router.push(`/${lng}${pathname}`);
      }
    };

    i18n.on('languageChanged', handleLanguageChange);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n, pathname, router]);

  return { i18n };
}

export default i18next;