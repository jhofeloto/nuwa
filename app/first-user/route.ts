import { z } from "zod";

import { prisma } from '@/prisma';
import { saltAndHashPassword } from "../lib/utils";


const users = [
  {
    id: '410544b2-4001-4271-9855-fec4b6a6442a',
    name: 'User',
    password: '123456',
    email: 'user@nuwa.com',
    role: 'GESTOR',
  },
  // Add more user objects as needed
];

// Define schema validation using Zod
const userSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  password: z.string(),
  email: z.string().email(),
  role: z.enum(["GESTOR", "ADMIN"]),
});

async function initDatabase() {
  try {
    console.log("Seeding database...");

    // ✅ Use Promise.all() to wait for all password hashes
    const hashedUsers = await Promise.all(
      users.map(async (user) => {
        const hashedPassword = await saltAndHashPassword(user.password);
        // const hashedPassword = await bcrypt.hash(user.password, 10);
        return userSchema.parse({ ...user, password: hashedPassword });
      })
    );

    await prisma.user.createMany({
      data: hashedUsers,
      skipDuplicates: true,
    });
    console.log("✅ Users seeded");

    // Add more seeding logic for other tables if needed
  } catch (error) {
    console.error("Seeding failed:", error);
  } finally {
    await prisma.$disconnect();
  }
}

export async function GET() {

  try {
    await initDatabase();

    return Response.json({ message: 'Database successfully initialized' });
  } catch (error) {
    return Response.json({ error }, { status: 500 });
  }
}