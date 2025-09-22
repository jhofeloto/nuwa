// app/api/getSpecies/route.ts
import { Prisma } from '@prisma/client';
import { NextResponse } from 'next/server';

import { prisma } from '@/prisma';

export async function GET() {
  try {
    const speciesList = await prisma.species.findMany({
      where: {
        AND: [
          { 
            values: {
              path: ['max_height', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['g_b', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['g_c', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['avg_dbh', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['g_b_dbh', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['g_c_dbh', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['allometric_coeff_a', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['allometric_coeff_b', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          },
          { 
            values: {
              path: ['r_coeff', 'value'],
              not: Prisma.JsonNullValueFilter.JsonNull
            }
          }
        ]
      },
      select: {
        common_name: true, // Only select the `common_name` field
      },
    });
    

    return NextResponse.json(speciesList.map((species) => species.common_name));
  } catch (error) {
    console.error('Error fetching species:', error);
    return NextResponse.json(
      { error: 'Failed to fetch species.' },
      { status: 500 }
    );
  }
}
