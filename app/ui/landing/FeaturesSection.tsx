'use client';

import { Button } from '@radix-ui/themes';
import { motion } from "framer-motion";
import Image from "next/image";
import { useTranslation } from "react-i18next";

const containerVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function FeaturesSection() {
  const { t, ready } = useTranslation('common');

  if (!ready) return null; // Ensure translations are ready before rendering

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      variants={containerVariants}
      className="py-24 px-6 sm:px-8 lg:px-12 xl:px-16 bg-white dark:bg-gray-900"
    >
      <div className="max-w-4xl xl:max-w-6xl mx-auto">
        <motion.h2
          variants={itemVariants}
          className="text-2xl font-semibold text-center mb-8 w-full sm:w-2/3 mx-auto"
        >
          {t('featureTitle')}
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12 xl:gap-16">
          {[0, 1, 2].map((index) => (
            <motion.div key={index} variants={itemVariants}>
              <FeatureCard
                imageSrc={
                  [
                    "/landing-carbon-feasibility.webp",
                    "/landing-carbon-assessment.webp",
                    "/landing-carbon-quantification.webp",
                  ][index]
                }
                title={t(`feature${index + 1}Title`)}
                description={t(`feature${index + 1}Description`)}
                linkText={t(`feature${index + 1}LinkText`)}
                linkHref={["/feasibility", "/assessment", "/quantification"][index]}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

const FeatureCard = ({
  imageSrc,
  title,
  description,
  linkText,
  linkHref,
}: {
  imageSrc: string;
  title: string;
  description: string;
  linkText: string;
  linkHref: string;
}) => (
  <div className="text-center">
    <div className="p-4 rounded-lg mb-4 flex items-center justify-center h-48">
      <Image
        src={imageSrc}
        width={400}
        height={400}
        className="w-full h-full object-contain"
        alt={title}
      />
    </div>
    <h3 className="text-lg font-medium mb-2">{title}</h3>
    <p className="text-sm mb-4">{description}</p>
    <Button
      size="2"
      variant="outline"
      onClick={() => window.location.href = linkHref}
      style={{
        borderColor: 'var(--mint-8)',
        color: 'var(--mint-9)',
        borderRadius: '0.375rem',
        cursor: 'pointer',
        backgroundColor: 'transparent',
        transition: 'all 0.2s ease-in-out'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--mint-3)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      {linkText}
    </Button>
  </div>
);