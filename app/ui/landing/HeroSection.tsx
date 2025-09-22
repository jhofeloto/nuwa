'use client';

import { Button } from '@radix-ui/themes';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { useTranslation } from 'react-i18next';

export default function HeroSection() {
    const { t, ready } = useTranslation('common');
    
    if (!ready) return null; // Ensure translations are ready before rendering
    
    return (
        <div className="relative h-screen">
            <Image src="/landing-splash.jpg" alt="Landing Image" fill className="object-cover object-center" priority />
            <div className="absolute inset-0 bg-black opacity-50"></div>
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="absolute top-1/3 transform -translate-x-1/2 -translate-y-1/2 text-center w-full"
            >
                <div className="max-w-4xl mx-auto px-16 sm:px-12">
                    <h1 className="text-5xl font-bold text-white mb-4">
                        {t('heroTitle')}
                    </h1>
                    <p className="text-xl text-white mb-8">
                        {t('heroDescription')}
                    </p>
                    
                    <div className="flex justify-center">
                        <Button 
                            size="3" 
                            className="px-6 py-3 text-base font-medium shadow-sm"
                            onClick={() => window.location.href = '/dashboard'}
                            style={{
                                backgroundColor: 'var(--mint-8)',
                                color: 'white',
                                borderRadius: '0.375rem',
                                transition: 'background-color 0.2s ease-in-out',
                                cursor: 'pointer',
                            }}
                            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'var(--mint-11)'}
                            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--mint-7)'}
                        >
                            {t('heroButton')}
                        </Button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}