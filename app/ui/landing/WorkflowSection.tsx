"use client";

import React from "react";
import { motion } from "framer-motion";
import { IconButton } from "@radix-ui/themes";
import { UploadIcon, ReaderIcon, BarChartIcon, BlendingModeIcon } from "@radix-ui/react-icons";
import { useTranslation } from "react-i18next";

const containerVariants = {
  hidden: { opacity: 0},
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1 },
};

export default function WorkflowSection() {
  const { t, ready } = useTranslation('common');

  if (!ready) return null; // Ensure translations are ready before rendering

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      variants={containerVariants}
      className="py-12 bg-stone-100 dark:bg-stone-900"
    >
      <div className="max-w-6xl xl:max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16">
        <motion.div variants={itemVariants} className="my-12 text-center">
          <h2 className="text-3xl font-semibold leading-tight text-gray-800 dark:text-gray-100">
            {t('workflowTitle')}
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            {t('workflowSubtitle')}
          </p>
          <p className="mt-2 max-w-3xl mx-auto text-gray-500 dark:text-gray-300">
            {t('workflowDescription')}
          </p>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12 xl:gap-16 text-center">
          {[0, 1, 2, 3].map((index) => (
            <motion.div key={index} variants={itemVariants}>
              <WorkFlowCard
                IconComponent={[UploadIcon, ReaderIcon, BarChartIcon, BlendingModeIcon][index]}
                width={30}
                height={30}
                title={t(`workflowStep${index + 1}Title`)}
                description={t(`workflowStep${index + 1}Description`)}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

const WorkFlowCard = ({
  IconComponent,
  width,
  height,
  title,
  description,
}: {
  IconComponent: React.ComponentType<{ width?: number; height?: number }>;
  width?: number;
  height?: number;
  title: string;
  description: string;
}) => (
  <div className="px-4 py-12 shadow-lg rounded-lg md:h-72 bg-primary-50 dark:bg-primary-900">
    <div className= "p-[0.6rem] rounded-full mb-4 h-10 w-10 mx-auto flex items-center justify-center">
      <IconButton>
        <IconComponent width={width} height={height} />
      </IconButton>
    </div>
    <h4 className="mt-4 text-xl font-medium text-gray-800 dark:text-gray-400">{title}</h4>
    <p className="mt-2 text-sm text-gray-500 dark:text-gray-300">{description}</p>
  </div>
);
