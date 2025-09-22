'use client';

import { useRouter } from 'next/navigation';
import i18next from '@/app/providers/i18n';
import { useEffect, useState } from 'react';

export default function LanguageToggle() {
  const router = useRouter();
  const [lang, setLang] = useState(i18next.language || 'en');

  const toggleLang = () => {
    const newLang = lang === 'en' ? 'es' : 'en';
    i18next.changeLanguage(newLang);
    setLang(newLang);
    router.refresh();
  };

  // Ensure state sync with i18next (when reloading page)
  useEffect(() => {
    setLang(i18next.language || 'en');
  }, []);

  return (
    <button
      onClick={toggleLang}
      className="flex items-center space-x-2 p-2 text-sm text-gray-300 hover:text-white"
    >
      {/* <GlobeIcon className="w-4 h-4" /> */}
      <span className="uppercase font-medium">
        {lang === 'en' ? 'EN 🇺🇸' : 'ES ᴄᴏ'}
      </span>
    </button>
  );
}
