import { prisma } from '@/prisma';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { selectedSpecies, selectedYear } = body;

    if (!selectedSpecies || selectedSpecies.length === 0) {
      return NextResponse.json(
        { error: 'No species selected.' },
        { status: 400 }
      );
    }
    if (!selectedYear) {
      return NextResponse.json(
        { error: 'No year selected.' },
        { status: 400 }
      );
    }

    const formattedSpeciesArray: string = `{${selectedSpecies.map((species: string) => `"${species}"`).join(',')}}`;

    // const temp = "Pino Caribe";
    const growthData = await prisma.$queryRaw`
    SELECT year, species, co2eq FROM generate_species_data(${formattedSpeciesArray}::text[], ${selectedYear}::int);
    `;

    return NextResponse.json(growthData);
  } catch (error) {
    console.error('Database Error:', error);
    return NextResponse.json({ error: 'Failed to fetch growth data.' }, { status: 500 });
  }
}
