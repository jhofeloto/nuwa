'use client';
import { useState, useEffect } from 'react';
import { Button } from "@/app/ui/button";
import { useTranslation } from 'react-i18next';

export default function GrowthParamsForm({
  onSubmit,
}: {
  onSubmit: (species: string[], year: number) => void;
}) {
  const { t } = useTranslation('common');
  const [selectedSpecies, setSelectedSpecies] = useState<string[]>([]);
  const [speciesOptions, setSpeciesOptions] = useState<string[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(5);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Fetch species options from the database
  useEffect(() => {
    async function fetchSpecies() {
      try {
        setIsLoading(true);
        const response = await fetch('/api/getSpecies');
        if (!response.ok) {
          throw new Error(t('FailedToFetchSpecies'));
        }

        const speciesList = await response.json();
        setSpeciesOptions(speciesList);
      } catch (error) {
        console.error('Error fetching species options:', error);
        setError(t('FailedToLoadSpecies'));
      } finally {
        setIsLoading(false);
      }
    }

    fetchSpecies();
  }, [t]);

  const handleSpeciesChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, (option) => option.value);
    setSelectedSpecies(selectedOptions);
  };

  const handleYearChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedYear(Number(event.target.value));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (selectedSpecies.length === 0) {
      setError(t('SelectAtLeastOneSpecies'));
      return;
    }
    if (!selectedYear) {
      setError(t('SelectOneYear'));
      return;
    }
    setError(null); 
    onSubmit(selectedSpecies, selectedYear); 
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="rounded-md border border-mint-6 dark:border-mint-8 overflow-hidden">
        <div className="rounded-md bg-gray-50 p-4 md:p-6 dark:bg-zinc-900">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Species Selection */}
            <div className="space-y-2">
              <label htmlFor="species" className="block text-mint-11 dark:text-mint-9 font-semibold">
                {t('SelectSpecies')}
              </label>
              {isLoading ? (
                <div className="h-10 w-full bg-mint-3 dark:bg-zinc-800 animate-pulse rounded-md"></div>
              ) : (
                <>
                  <select
                    id="species"
                    name="species"
                    multiple
                    className="block w-full h-32 text-mint-11 dark:text-mint-9 border-mint-6 dark:border-mint-8 rounded-md border py-2 pl-3 pr-10 text-sm focus:ring-2 focus:ring-mint-6 dark:focus:ring-mint-8 focus:border-mint-6 dark:focus:border-mint-8 bg-white dark:bg-zinc-800 transition-colors"
                    value={selectedSpecies}
                    onChange={handleSpeciesChange}
                  >
                    {speciesOptions.map((species) => (
                      <option key={species} value={species}>
                        {species}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-mint-11 dark:text-mint-9 opacity-70">
                    {t('MultipleOptions')}
                  </p>
                </>
              )}
            </div>

            {/* Year Selection */}
            <div className="space-y-2">
              <label htmlFor="year" className="block text-mint-11 dark:text-mint-9 font-semibold">
                {t('SelectYear')}
              </label>
              <select
                id="year"
                name="year"
                className="block w-full text-mint-11 dark:text-mint-9 rounded-md border border-mint-6 dark:border-mint-8 py-2 pl-3 pr-10 text-sm focus:ring-2 focus:ring-mint-6 dark:focus:ring-mint-8 focus:border-mint-6 dark:focus:border-mint-8 bg-white dark:bg-zinc-800 transition-colors"
                value={selectedYear}
                onChange={handleYearChange}
              >
                {[5, 10, 15, 20, 25, 30, 35, 40, 45, 50].map((year) => (
                  <option key={year} value={year}>
                    {t('{{year}} years', { year })}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {error && (
            <div className="mt-4 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}
          
          <div className="mt-6 flex justify-end">
            <Button 
              variant="outline" 
              type="submit" 
              className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
            >
              {t('GenerateGrowthTrend')}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}