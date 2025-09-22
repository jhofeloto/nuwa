"use client"

import { ColumnDef } from "@tanstack/react-table"
import { useTranslation } from "react-i18next"
import ProjectStatus from "@/app/ui/dashboard/project-status"
import Link from "next/link"

import { Growth } from "@/app/lib/definitions";

// Helper function to get translated column headers
const getColumnHeaders = (t: (key: string) => string) => ({
  details: t('columnProjectDetails'),
  status: t('columnStatus'),
  name: t('columnName'),
  title: t('columnTitle'),
  country: t('columnCountry'),
  department: t('columnDepartment'),
  investment: t('columnInvestment'),
  impact: t('columnImpact'),
  bankableInvestment: t('columnBankableInvestment'),
  income: t('columnIncome'),
  treeQuantity: t('columnTreeQuantity'),
  tokenGranularity: t('columnTokenGranularity'),
  lands: t('columnLands'),
  abstract: t('columnAbstract'),
  polygone: t('columnPolygone'),
  geolocationPoint: t('columnGeolocationPoint'),
  investmentTeaser: t('columnInvestmentTeaser'),
  createdAt: t('columnCreatedAt'),
  updatedAt: t('columnUpdatedAt'),
  description: t('columnDescription'),
});

// Convert to a custom hook
export function useProjectColumns(): ColumnDef<Growth>[] {
  const { t } = useTranslation('common');
  const headers = getColumnHeaders(t);

  return [
    {
      accessorKey: "details",
      header: headers.details,
      cell: ({ row }) => (
        <Link href={`./dashboard/project/${row.original.id}`} className="text-blue-600 hover:underline">
          {t('viewDetails')}
        </Link>
      ),
    },
    {
      accessorKey: "status",
      header: headers.status,
      cell: ({ row }) => <ProjectStatus status={row.original.status} />,
    },
    {
      accessorKey: "name",
      header: headers.name,
    },
    {
      accessorKey: "title",
      header: headers.title,
    },
    {
      accessorKey: "country",
      header: headers.country,
    },
    {
      accessorKey: "department",
      header: headers.department,
    },
    {
      accessorKey: "investment",
      header: headers.investment,
      cell: ({ row }) => {
        const value = row.original.values.total_investment?.value ?? 0;
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
      },
    },
    {
      accessorKey: "impact",
      header: headers.impact,
      cell: ({ row }) => {
        const value = row.original.values.impact?.value ?? 0;
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
      },
    },
    {
      accessorKey: "bankableInvestment",
      header: headers.bankableInvestment,
      cell: ({ row }) => {
        const value = row.original.values.bankable_investment?.value ?? 0;
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
      },
    },
    {
      accessorKey: "income",
      header: headers.income,
      cell: ({ row }) => {
        const value = row.original.values.income?.value ?? 0;
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
      },
    },
    {
      accessorKey: "treeQuantity",
      header: headers.treeQuantity,
      cell: ({ row }) => {
        const value = row.original.values.tree_quantity?.value ?? 0;
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
      },
    },
    {
      accessorKey: "tokenGranularity",
      header: headers.tokenGranularity,
      cell: ({ row }) => {
        const value = row.original.values.token_granularity?.value ?? 0;
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
      },
    },
    {
      accessorKey: "lands",
      header: headers.lands,
      cell: ({ row }) => {
        const value = row.original.values.lands?.value ?? 0;
        return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
      },
    },
    {
      accessorKey: "abstract",
      header: headers.abstract,
      cell: ({ row }) => row.original.values.abstract?.value ?? "",
    },
    {
      accessorKey: "polygone",
      header: headers.polygone,
      cell: ({ row }) => row.original.values.polygone?.value ?? "",
    },
    {
      accessorKey: "geolocation_point",
      header: headers.geolocationPoint,
      cell: ({ row }) => row.original.values.geolocation_point?.value ?? "",
    },
    {
      accessorKey: "investment_teaser",
      header: headers.investmentTeaser,
      cell: ({ row }) => row.original.values.investment_teaser?.value ?? "",
    },
    {
      accessorKey: "createdAt",
      header: headers.createdAt,
      cell: ({ row }) => {
        const date = new Date(row.original.createdAt);
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
        }).format(date);
      },
    },
    {
      accessorKey: "updatedAt",
      header: headers.updatedAt,
      cell: ({ row }) => {
        const date = new Date(row.original.updatedAt);
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
        }).format(date);
      },
    },
    {
      accessorKey: "description",
      header: headers.description,
    },
  ];
}