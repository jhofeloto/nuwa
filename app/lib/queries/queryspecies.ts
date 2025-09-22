
import { prisma } from '@/prisma';

import { State } from '@/app/lib/definitions';

export async function querySpecies(prevState: State, formData: FormData) {
  const species = formData.get('species') as string;

  if (!species) {
    return { errors: { species: ['Species is required.'] } };
  }

  try {
    const growthData: { month: string; growth: number }[] = await prisma.$queryRaw`
      SELECT * FROM generate_species_data(${species}::text, 10);
    `;
    return { growthData };
  } catch (error) {
    console.error('Database Error:', error);
    throw new Error('Failed to fetch growth data.');
  }
}
