import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

if (!i18next.isInitialized) {
  i18next
    .use(HttpBackend) // Load translations from /public/locales
    .use(LanguageDetector) // Detect browser language
    .use(initReactI18next)
    .init({
      fallbackLng: 'en',
      supportedLngs: ['en', 'es'],
      // debug: process.env.NODE_ENV === 'development', // Enable debug mode only in development
      detection: {
        order: ['cookie', 'localStorage', 'navigator'],
        caches: ['cookie'],
      },
      backend: {
        loadPath: '/locales/{{lng}}/{{ns}}.json', // Ensure this matches the public/locales structure
      },
      ns: ['common'],
      defaultNS: 'common',
      react: { useSuspense: false },
    });
}

export default i18next;
