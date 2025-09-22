import { NextResponse } from "next/server";
import ExcelJS from "exceljs";
import fs from "fs";
import { ecosystemsParser, keywordsParser, mathModelsParser, projectsParser, saveFile, speciesParser, parcelsParser, coverageParser, parcelAnalysisParser } from "@/app/lib/seed/helper";

export const config = {
  api: { bodyParser: false },
};
import { prisma } from '@/prisma';

function handleError(error: unknown): NextResponse {
  console.error("❌ Error processing:", error);
  let message = "Unknown error";

  if (error instanceof Error) {
    message = error.message;

    // Extract Prisma-specific error message
    const prismaErrorMatch = message.match(/Argument `(.+?)`: Invalid value provided. Expected (.+?), provided (.+?)\./);
    if (prismaErrorMatch) {
      message = `Invalid value for argument \`${prismaErrorMatch[1]}\`. Expected ${prismaErrorMatch[2]}, provided ${prismaErrorMatch[3]}.`;
    }
  }

  return NextResponse.json({ message }, { status: 400 });
}

// ✅ Named export for POST method (Next.js App Router)
export async function POST(req: Request) {
  try {
    // Extract file from formData
    const formData = await req.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json({ message: "No file uploaded" }, { status: 400 });
    }

    // Save the file to /tmp
    const filePath = await saveFile(file);

    // Read the Excel file
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(filePath);

    for (const worksheet of workbook.worksheets) {
      const sheetName = worksheet.name;

      try {
        if (sheetName === "MathModels") {
          const validatedMathModels = mathModelsParser(worksheet);

          await prisma.mathModels.createMany({
            data: validatedMathModels,
            skipDuplicates: true,
          });

          console.log("✅ MathModels inserted successfully:", validatedMathModels);
        } else if (sheetName === "Species") {
          const validatedSpecies = speciesParser(worksheet);

          // Check for missing mandatory fields
          for (const species of validatedSpecies) {
            if (!species.common_name || !species.scientific_name) {
              return NextResponse.json({ message: "Missing mandatory fields: common_name and scientific_name are required" }, { status: 400 });
            }
          }

          await prisma.species.createMany({
            data: validatedSpecies,
            skipDuplicates: true,
          });

          console.log("✅ Species inserted successfully:", validatedSpecies);
        } else if (sheetName === "Keywords") {
          const validatedKeywords = keywordsParser(worksheet);

          await prisma.keyword.createMany({
            data: validatedKeywords,
            skipDuplicates: true,
          });

          console.log("✅ Keywords inserted successfully:", validatedKeywords);
        } else if (sheetName === "Ecosystem") {
          const ecosystems = ecosystemsParser(worksheet);

          // ✅ Insert ecosystems into Prisma
          await prisma.ecosystem.createMany({
            data: ecosystems,
            skipDuplicates: true,
          });

          console.log("✅ Ecosystems inserted successfully:", ecosystems);
        } else if (sheetName === "Project") {
          const projects = await projectsParser(worksheet);

          // Check for missing mandatory fields
          for (const project of projects) {
            if (!project.name || !project.title) {
              return NextResponse.json({ message: "Missing mandatory fields: name and title are required" }, { status: 400 });
            }
          }

          await Promise.all(
            projects.map(async (project) => {
              // ✅ Upsert project into Prisma
              await prisma.project.upsert({
                where: { name: project.name }, // Assuming id is unique
                update: {}, // No update if it exists
                create: project,
              });
            })
          );

          console.log("✅ Projects inserted successfully:", projects);
        } else if (sheetName === "Parcels") {
          const parcels = await parcelsParser(worksheet);

          // Check for missing mandatory fields
          for (const parcel of parcels) {
            if (!parcel.name || !parcel.speciesId) {
              return NextResponse.json({ message: "Missing mandatory fields: name and speciesId are required" }, { status: 400 });
            }
          }

          // ✅ Insert parcel into Prisma
          await prisma.parcels.createMany({
            data: parcels,
            skipDuplicates: true,
          });

          console.log("✅ Parcels inserted successfully:", parcels);
        } else if (sheetName === "Coverage") {
          const coverage = await coverageParser(worksheet);

          // ✅ Insert coverage into Prisma
          await prisma.coverage.createMany({
            data: coverage,
            skipDuplicates: true,
          });

          console.log("✅ Coverage inserted successfully:", coverage);
        } else if (sheetName === "ParcelAnalysis") {
          const parcelAnalysis = await parcelAnalysisParser(worksheet);

          // Check for missing mandatory fields
          for (const analysis of parcelAnalysis) {
            if (!analysis.parcelId || !analysis.analysisType) {
              return NextResponse.json({ message: "Missing mandatory fields: parcelId and analysisType are required" }, { status: 400 });
            }
          }

          // ✅ Insert parcelAnalysis into Prisma
          await prisma.parcelAnalysis.createMany({
            data: parcelAnalysis,
            skipDuplicates: true,
          });

          console.log("✅ ParcelAnalysis inserted successfully:", parcelAnalysis);
        }


      } catch (error) {
        return handleError(error);
      }
    }

    await prisma.$executeRawUnsafe(`CALL parcels_agbs_calculations_materialized()`);
    await prisma.$executeRawUnsafe(`CALL parcels_co2eq_materialized()`);

    // ✅ Delete file after processing
    await fs.promises.unlink(filePath);
    console.log(`Deleted file: ${filePath}`);

    return NextResponse.json({ message: "Database seeded successfully!" });
  } catch (error) {
    return handleError(error);
  }
}
