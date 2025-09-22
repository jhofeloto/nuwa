'use client';

import { Button } from '@radix-ui/themes';
import { useTranslation } from "react-i18next";

export default function CallToActionSection() {
    const { t, ready } = useTranslation('common');
    
    if (!ready) return null; // Ensure translations are ready before rendering
    
    return (
        <div className="py-12 bg-stone-100 dark:bg-stone-900">
            <div className="max-w-6xl xl:max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16">
                <div className="my-12 text-center">
                    <h2 className="text-3xl font-semibold leading-tight text-gray-800 dark:text-gray-100">
                        {t('callToActionTitle')}
                    </h2>
                    <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
                        {t('callToActionSubtitle')}
                    </p>
                    <p className="mt-2 max-w-3xl mx-auto text-gray-500 dark:text-gray-300">
                        {t('callToActionDescription')}
                    </p>
                </div>
                <div className="flex justify-center">
                    <Button 
                        size="3"
                        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                        style={{
                            backgroundColor: 'var(--mint-8)',
                            color: 'white',
                            borderRadius: '0.375rem',
                            padding: '0.75rem 1.5rem',
                            fontSize: '1rem',
                            fontWeight: '500',
                            cursor: 'pointer',
                            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                            transition: 'background-color 0.2s ease-in-out'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'var(--mint-11)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--mint-7)'}
                    >
                        {t('callToActionButton')}
                    </Button>
                </div>
                <div className="mt-8 text-center">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        {t('callToActionFooter')}{" "}
                        <a 
                            href="/login" 
                            className="text-mint-9 hover:text-mint-10"
                            style={{ color: 'var(--mint-9)', transition: 'color 0.2s ease-in-out' }}
                            onMouseOver={(e) => e.currentTarget.style.color = 'var(--mint-10)'}
                            onMouseOut={(e) => e.currentTarget.style.color = 'var(--mint-9)'}
                        >
                            {t('callToActionLogin')}
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
}