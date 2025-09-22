"use client"

import { useState } from 'react';
import { useProjectColumns } from './columns';
import { DataTable } from './data-table';
import { Growth } from '@/app/lib/definitions';

interface ProjectTableClientProps {
  initialData: Growth[];
}

export function ProjectTableClient({ initialData }: ProjectTableClientProps) {
  // Format dates if needed (since they might be serialized when passed from server to client)
  const formattedData = initialData.map(item => ({
    ...item,
    // Ensure dates are Date objects (in case they were serialized to strings)
    createdAt: item.createdAt instanceof Date ? item.createdAt : new Date(item.createdAt),
    updatedAt: item.updatedAt instanceof Date ? item.updatedAt : new Date(item.updatedAt),
    // Ensure values has the right structure
    values: {
      total_investment: { value: item.values?.total_investment?.value ?? 0 },
      impact: { value: item.values?.impact?.value ?? 0 },
      bankable_investment: { value: item.values?.bankable_investment?.value ?? 0 },
      income: { value: item.values?.income?.value ?? 0 },
      tree_quantity: { value: item.values?.tree_quantity?.value ?? 0 },
      lands: { value: item.values?.lands?.value ?? 0 },
      abstract: { value: item.values?.abstract?.value ?? '' },
      polygone: { value: item.values?.polygone?.value ?? '' },
      geolocation_point: { value: item.values?.geolocation_point?.value ?? '' },
      investment_teaser: { value: item.values?.investment_teaser?.value ?? '' },
      token_granularity: { value: item.values?.token_granularity?.value ?? 0 },
    }
  }));

  // Store the formatted data in state
  const [projectData] = useState<Growth[]>(formattedData);
  
  // Get columns using the custom hook
  const columns = useProjectColumns();

  return <DataTable columns={columns} data={projectData} />;
}