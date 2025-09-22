'use client';
import { useState, useEffect } from 'react';
import GrowthChart from './growth-chart';
import GrowthParamsForm from './growth-params-form';
import GrowthTable from './growth-table';
import Pagination from './pagination';
import { GrowthData } from '@/app/lib/definitions';
import { useTranslation } from 'react-i18next';
import Breadcrumbs from '../breadcrumbs';
import { lusitana } from '../fonts';

const convertToPlainObject = (value: { toNumber?: () => number } | number): number => {
  if (value && typeof value === 'object' && 'toNumber' in value) {
    return value.toNumber ? value.toNumber() : Number(value); // Convert Prisma Decimal to number
  }
  return typeof value === 'number' ? value : Number(value);
};

const formatGrowthData = (growthData: GrowthData[]) => {
  // Group data by species
  const groupedData = growthData.reduce((acc: { [key: string]: { x: number; y: number }[] }, curr) => {
    if (!acc[curr.species]) {
      acc[curr.species] = [];
    }
    acc[curr.species].push({
      x: curr.year,
      y: convertToPlainObject(curr.co2eq),
    });
    return acc;
  }, {});

  // Convert grouped data into Nivo-compatible format
  return Object.keys(groupedData).map((species) => ({
    id: species,
    data: groupedData[species],
  }));
};

export default function GrowthComponent() {
  const { t } = useTranslation('common');
  const [growthData, setGrowthData] = useState<GrowthData[]>([]);
  const [activeTab, setActiveTab] = useState<'table' | 'chart'>('chart');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (selectedSpecies: string[], selectedYear: number) => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/getGrowCurves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedSpecies, selectedYear }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch growth data');
      }

      const data = await response.json();
      setGrowthData(data);
      
      // Calculate total items for pagination
      const totalItems = data.reduce((count: number, species: { co2eq?: { length: number }[] }) => {
        return count + (species.co2eq ? species.co2eq.length : 0);
      }, 0);
      
      // Use 15 items per page (matching the GrowthTable's recordsPerPage)
      setTotalPages(Math.ceil(totalItems / 15));
      setCurrentPage(1); // Reset to first page when new data is loaded
    } catch (error) {
      console.error('Error fetching growth data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formattedData = formatGrowthData(growthData);
  
  // Calculate actual total data items for pagination
  const totalDataItems = formattedData.reduce((count, species) => {
    return count + species.data.length;
  }, 0);
  
  // Ensure total pages is correctly set based on formatted data
  useEffect(() => {
    if (formattedData.length > 0) {
      const recordsPerPage = 15; // Same as in GrowthTable
      const calculatedPages = Math.max(1, Math.ceil(totalDataItems / recordsPerPage));
      
      if (calculatedPages !== totalPages) {
        setTotalPages(calculatedPages);
        // Also reset to page 1 if current page is now invalid
        if (currentPage > calculatedPages) {
          setCurrentPage(1);
        }
      }
    }
  }, [formattedData, totalDataItems, currentPage, totalPages]);

  return (
    <div>
      <Breadcrumbs
        breadcrumbs={[
          { label: t('breadcrumbHome'), href: '/' },
          { label: t('breadcrumbGrowth'), href: '/growth', active: true }
        ]}
      />
      <h1 className={`${lusitana.className} mb-6 text-2xl md:text-3xl font-bold text-mint-11 dark:text-mint-9`}>
      {t('growthModels')}
      </h1>
    <div className="w-full space-y-6">
      <GrowthParamsForm onSubmit={handleSubmit} />
      
      {isLoading && (
        <div className="w-full flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-mint-9"></div>
        </div>
      )}

      {!isLoading && formattedData.length > 0 && (
        <div className="w-full rounded-md border border-mint-6 dark:border-mint-8 overflow-hidden bg-gray-50 p-4 md:p-6 dark:bg-zinc-900">
          <div className="flex border-b border-mint-6 dark:border-mint-8 mb-4">
            <button
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'chart' 
                  ? 'border-b-2 border-mint-9 text-mint-11 dark:text-mint-9' 
                  : 'text-gray-500 hover:text-mint-11 dark:hover:text-mint-9'
              }`}
              onClick={() => setActiveTab('chart')}
            >
              {t('Graph')}
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'table' 
                  ? 'border-b-2 border-mint-9 text-mint-11 dark:text-mint-9' 
                  : 'text-gray-500 hover:text-mint-11 dark:hover:text-mint-9'
              }`}
              onClick={() => setActiveTab('table')}
            >
              {t('Table')}
            </button>
          </div>

          {/* Tab Content */}
          <div className="mt-4">
            {activeTab === 'chart' && (
              <div className="w-full h-[400px] md:h-[500px] lg:h-[600px]">
                <GrowthChart data={formattedData} />
              </div>
            )}
            
            {activeTab === 'table' && (
              <div className="space-y-4">
                <div className="w-full overflow-x-auto">
                  <GrowthTable data={formattedData} currentPage={currentPage} />
                </div>
                <div className="flex justify-center mt-4">
                  <Pagination 
                    totalPages={totalPages} 
                    currentPage={currentPage} 
                    onPageChange={setCurrentPage} 
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
    </div>
  );
}