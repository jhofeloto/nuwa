// app/api/generate-population/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/prisma';

interface Event {
  year: string;
  percentage: string;
}

interface PopulationResult {
  year: number;
  population: number;
}

export async function POST(request: NextRequest) {
  const { projectId, species, startDate, endDate, events }: {
    projectId: string;
    species: string;
    startDate: string;
    endDate: string;
    events: Event[];
  } = await request.json();

  try {
    // Convert events array to JSON string
    const eventsJson = JSON.stringify(events);

    // Call the PostgreSQL function using Prisma's $queryRaw
    const populationTable = await prisma.$queryRaw<PopulationResult[]>`
      SELECT * FROM generate_growth_project(
        ${projectId}::UUID,
        ${species},
        ${startDate}::DATE,
        ${endDate}::DATE,
        ${eventsJson}::JSON
      )
    `;

    return NextResponse.json(populationTable);
  } catch (error) {
    console.error('Error calling generate_growth_project:', error);
    return NextResponse.json(
      { error: 'Failed to generate growth project table' },
      { status: 500 }
    );
  }
}