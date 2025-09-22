import { Prisma } from '@prisma/client';

import { TotalImpactResult, TotalInvestmentResult, TotalBankableInvestmentResult, TotalIncomeResult } from '../definitions';

import { prisma } from '@/prisma';

export async function fetchCardData() {

    try {

      const totalInvestmentPromise = prisma.$queryRaw<TotalInvestmentResult[]>`
      SELECT * FROM total_investment;
      `;
      const TotalImpactPromise = prisma.$queryRaw<TotalImpactResult[]>`
        SELECT * FROM total_impact;
      `;
      const totalBankableInvestmentPromise = prisma.$queryRaw<TotalBankableInvestmentResult[]>`
        SELECT * FROM total_bankable_investment;
      `;
      const totalIncomePromise = prisma.$queryRaw<TotalIncomeResult[]>`
        SELECT * FROM total_income;
      `;
      const grandTotalCo2Promise = prisma.$queryRaw<{ grand_total_co2: Prisma.Decimal; grand_total_area: Prisma.Decimal }[]>(
        Prisma.sql`SELECT * FROM sum_all_parcels_agbs_totals()`
      );

      const CO2Promise = await prisma.$queryRaw<{ sum_co2_total: Prisma.Decimal; average_co2_total: Prisma.Decimal }[]>(
        Prisma.sql`SELECT * FROM avg_all_parcels_co2eq_totals()`
      );

      const landNumberPromise = prisma.parcels.count();

      const data = await Promise.all([
        TotalImpactPromise,
        totalInvestmentPromise,
        totalBankableInvestmentPromise,
        totalIncomePromise,
        landNumberPromise,
        grandTotalCo2Promise,
        CO2Promise,
      ]);

      const totalImpact = Number((data[0] as TotalImpactResult[])[0]?.total_impact);
      const totalInvestment = Number((data[1] as TotalInvestmentResult[])[0]?.total_investment);
      const totalBankableInvestment = Number((data[2] as TotalBankableInvestmentResult[])[0]?.total_bankable_investment);
      const totalIncome = Number((data[3] as TotalIncomeResult[])[0]?.total_income);
      const landNumber = Number(data[4]);
      const totalco2 = data[5][0]?.grand_total_co2?.toNumber() ?? 0;
      const area = data[5][0]?.grand_total_area?.toNumber() ?? 0;

      const sumCo2Total = data[6][0]?.sum_co2_total?.toNumber() ?? 0;
      const averageCo2Total = data[6][0]?.average_co2_total?.toNumber() ?? 0;

    return { totalImpact, totalInvestment, totalBankableInvestment, totalIncome, landNumber, totalco2, area, averageCo2Total, sumCo2Total, projectName: 'ALL PROJECTS' };

    } catch (error) {
      console.error('Database Error:', error);
      throw new Error('Failed to fetch card data.');
    }
  }

  export async function fetchProjectData() {
    try {
      const projectsData = await prisma.project.findMany();

      return projectsData;
    } catch (error) {
      console.error('Database Error:', error);
      throw new Error('Failed to fetch growth data.');
    }
  }

  export async function fetchSpeciesByProjectId(projectId: string) {
    try {
      const uniqueSpecies = await prisma.species.findMany({
        distinct: ['common_name'], // Ensures unique species based on common_name
        select: {
          common_name: true
        },
        where: {
          parcels: {
            some: {
              projectId: projectId
            }
          }
        }
      }).then(results => results.map(result => result.common_name));

      return uniqueSpecies;
    } catch (error) {
      console.error('Database Error:', error);
      throw new Error('Failed to fetch species data.');
    }
  }

  export async function fetchProjectById(id: string) {
    try {
      const projectData = await prisma.project.findUnique({
        where: { id },
        select: {
          name: true,
          values: true,
        },
      }) as { name: string
        values: { impact?: { value: number }
              total_investment?: { value: number }
              bankable_investment?: { value: number }
              income?: { value: number }
            } 
        };

      if (!projectData || !projectData.values) {
        throw new Error('Project data not found or values field is empty.');
      }

      const landNumber = await prisma.parcels.count({
        where: {
          projectId: id,
        },
      });

      const tableName = `parcels_agbs_project_${id.replace(/-/g, '').substring(0, 20)}`;
      
      const [parcelco2total] = await prisma.$queryRaw<{ totalco2: number; area: number }[]>(
        Prisma.sql`SELECT SUM(parcel_co2eq_total) as totalco2, SUM(area) as area FROM ${Prisma.raw(tableName)}`
      );
      
      
      const totalco2 = parcelco2total?.totalco2 ? Number(parcelco2total.totalco2) : 0;
      const area = parcelco2total?.area ? Number(parcelco2total.area) : 0;
      
      const tableNameCo2 = `parcels_co2eq_project_${id.replace(/-/g, '').substring(0, 20)}`;

      const result = await prisma.$queryRaw<{ sum_co2_total: Prisma.Decimal; average_co2_total: Prisma.Decimal }[]>(
        Prisma.sql`
          SELECT SUM(co2Total) as sum_co2_total, AVG(co2TotalArea) as average_co2_total
          FROM (
            SELECT parcel_name, SUM(co2eq_ton) as co2Total, (SUM(co2eq_ton) / p.area) as co2TotalArea
            FROM ${Prisma.raw(tableNameCo2)} as co2parcel
            LEFT JOIN public."Parcels" as p ON co2parcel.parcel_id = p.id
            GROUP BY parcel_name, area
          ) as subquery
        `
      );
      
      const sumCo2Total = result[0]?.sum_co2_total?.toNumber() ?? 0;
      const averageCo2Total = result[0]?.average_co2_total?.toNumber() ?? 0;

      const totalImpact = Number(projectData.values.impact?.value || 0);
      const totalInvestment = Number(projectData.values.total_investment?.value || 0);
      const totalBankableInvestment = Number(projectData.values.bankable_investment?.value || 0);
      const totalIncome = Number(projectData.values.income?.value || 0);
    
      return { totalImpact, totalInvestment, totalBankableInvestment, totalIncome, landNumber, totalco2, area, averageCo2Total, sumCo2Total, projectName: projectData.name };
    } catch (error) {
      console.error('Database Error:', error);
      throw new Error('Failed to fetch project data.');
    }
  }