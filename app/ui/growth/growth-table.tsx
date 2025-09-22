'use client';
import React from 'react';
import { useTranslation } from 'react-i18next';

interface GrowthTableProps {
  data: {
    id: string;
    data: { x: number; y: number }[];
  }[];
  currentPage: number;
}

const GrowthTable: React.FC<GrowthTableProps> = ({ data, currentPage }) => {
  const { t } = useTranslation('common');

  if (!data || data.length === 0) {
    return (
      <div className="w-full py-12 flex justify-center items-center">
        <p className="text-center text-mint-11 dark:text-mint-9 opacity-70">{t('NoDataAvailable')}</p>
      </div>
    );
  }

  const recordsPerPage = 15;
  const startIndex = (currentPage - 1) * recordsPerPage;
  const endIndex = startIndex + recordsPerPage;
  
  // Create flattened array of all data points
  const allData = data.flatMap((item) =>
    item.data.map((record) => ({
      species: item.id,
      year: record.x,
      co2eq: record.y,
    }))
  );
  
  // Sort by species and then by year for consistent ordering
  allData.sort((a, b) => {
    if (a.species !== b.species) {
      return a.species.localeCompare(b.species);
    }
    return a.year - b.year;
  });
  
  // Get current page data
  const paginatedData = allData.slice(startIndex, endIndex);

  return (
    <div className="w-full">
      {/* Mobile-friendly version */}
      <div className="md:hidden space-y-3">
        {paginatedData.map((record, index) => (
          <div
            key={`${record.species}-${record.year}-${index}`}
            className="w-full rounded-md bg-white dark:bg-zinc-800 p-4 border border-mint-6 dark:border-mint-8 shadow-sm"
          >
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-xs font-medium text-mint-11 dark:text-mint-9">{t('Species')}</p>
                <p className="text-sm text-gray-900 dark:text-gray-100 font-medium">{record.species}</p>
              </div>
              
              <div className="space-y-1">
                <p className="text-xs font-medium text-mint-11 dark:text-mint-9">{t('year')}</p>
                <p className="text-sm text-gray-900 dark:text-gray-100">{record.year}</p>
              </div>
              
              <div className="col-span-2 pt-2 border-t border-mint-6/20 dark:border-mint-8/20 space-y-1">
                <p className="text-xs font-medium text-mint-11 dark:text-mint-9">{t('CO2eq')} (kg)</p>
                <p className="text-sm text-gray-900 dark:text-gray-100 font-medium">{record.co2eq.toFixed(2)}</p>
              </div>
            </div>
          </div>
        ))}
        
        {paginatedData.length === 0 && (
          <div className="w-full py-8 text-center text-sm text-mint-11 dark:text-mint-9 opacity-70">
            {t('NoResultsForThisPage')}
          </div>
        )}
      </div>

      {/* Desktop version */}
      <div className="hidden md:block overflow-hidden rounded-lg border border-mint-6 dark:border-mint-8">
        <table className="min-w-full divide-y divide-mint-6 dark:divide-mint-8">
          <thead className="bg-mint-3 dark:bg-zinc-800">
            <tr>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-mint-11 dark:text-mint-9 uppercase tracking-wider"
              >
                {t('Species')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-mint-11 dark:text-mint-9 uppercase tracking-wider"
              >
                {t('year')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-mint-11 dark:text-mint-9 uppercase tracking-wider"
              >
                {t('CO2eq')} (kg)
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-zinc-900 divide-y divide-mint-6/20 dark:divide-mint-8/20">
            {paginatedData.map((record, index) => (
              <tr 
                key={`${record.species}-${record.year}-${index}`}
                className="hover:bg-mint-1 dark:hover:bg-zinc-800/50 transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                  {record.species}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  {record.year}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                  {record.co2eq.toFixed(2)}
                </td>
              </tr>
            ))}
            
            {paginatedData.length === 0 && (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-sm text-mint-11 dark:text-mint-9 opacity-70">
                  {t('NoResultsForThisPage')}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 text-xs text-center text-mint-11 dark:text-mint-9">
        {paginatedData.length > 0 ? (
          <>
            {t('ShowingPage', { currentPage })} · {t('Records', { count: paginatedData.length })}
          </>
        ) : (
          <>{t('NoDataToDisplay')}</>
        )}
      </div>
    </div>
  );
};

export default GrowthTable;