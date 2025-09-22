import { Prisma } from "@prisma/client";
import { NextResponse } from "next/server";
import { ParcelData, EcosystemData, TreeNode, ParcelCo2Data } from "@/app/lib/definitions";

import { prisma } from '@/prisma';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { projectIds, queryType } = body;

    if (!projectIds || projectIds.length === 0) {
      return NextResponse.json(
        { error: "No project selected." },
        { status: 400 }
      );
    }

    if (!queryType || !["aggregated", "details", "co2"].includes(queryType)) {
      return NextResponse.json(
        { error: "Invalid query type. Use 'aggregated', 'details', or 'co2'." },
        { status: 400 }
      );
    }

    let responseData;

    if (queryType === "aggregated") {
      const projectId = projectIds[0]; // Assuming a single project ID for aggregated query
      const tableName = `parcels_agbs_project_${projectId.replace(/-/g, '').substring(0, 20)}`;

      const aggregatedData: EcosystemData[] = await prisma.$queryRaw(
        Prisma.sql`
          SELECT ecosystem,
                 SUM(parcel_bgb) AS bgb,
                 SUM(parcel_co2eq_captured) AS co2,
                 SUM(parcel_agb) AS agb,
                 SUM(parcel_soc_total) AS soc
            FROM ${Prisma.raw(tableName)}
           GROUP BY ecosystem
        `
      );



      responseData = aggregatedData.map((parcel: EcosystemData) => ({
        ecosystem: parcel.ecosystem,
        bgb: parcel.bgb,
        co2: parcel.co2,
        agb: parcel.agb,
        soc: parcel.soc
      }));

    } else if (queryType === "details") {
      // Query for detailed parcels info
      const parcelsData: ParcelData[] = await prisma.$queryRaw`
        SELECT p.name AS project,
               pa.department,
               e.type AS ecosystem,
               s.common_name AS species,
               pa.name AS parcelname,
               pa.id AS parcelId,
               pa.area
          FROM "Parcels" pa
          JOIN "Project" p ON pa."projectId" = p.id
          LEFT JOIN "Ecosystem" e ON pa."ecosystemId" = e.id
          LEFT JOIN "Species" s ON pa."speciesId" = s.id
         WHERE p.id = ANY(${projectIds}::uuid[]);
      `;

      responseData = formatTreeMapData(parcelsData);

    } else if (queryType === "co2") {
      const projectId = projectIds[0]; // Assuming a single project ID for CO2 query
      const tableName = `parcels_co2eq_project_${projectId.replace(/-/g, '').substring(0, 20)}`;

      // Query for CO2 data grouped by year, ecosystem, and species
      const co2Data: ParcelCo2Data[] = await prisma.$queryRaw`
        SELECT ecosystem,
               species,
               year,
               SUM(co2eq_ton) AS co2total
          FROM ${Prisma.raw(tableName)}
         GROUP BY year, ecosystem, species
         ORDER BY year, ecosystem, species;
      `;

      responseData = co2Data;
    }

    // Ensure responseData is JSON serializable
    return NextResponse.json(JSON.parse(JSON.stringify(responseData)));
  } catch (error) {
    console.error("Database Error:", error);
    return NextResponse.json(
      { error: "Failed to fetch parcels data." },
      { status: 500 }
    );
  }
}

function formatTreeMapData(data: ParcelData[]): TreeNode {
  const treeMapData: TreeNode = { name: "Projects", children: [] };

  const projectMap = new Map<string, TreeNode>();

  data.forEach((item) => {
    if (!projectMap.has(item.project)) {
      projectMap.set(item.project, { name: item.project, children: [], total: 0 });
      treeMapData.children!.push(projectMap.get(item.project)!);
    }

    const projectNode = projectMap.get(item.project)!;
    projectNode.total! += item.area;

    let departmentNode = projectNode.children!.find((d) => d.name === item.department);

    if (!departmentNode) {
      departmentNode = { name: item.department, children: [], total: 0 };
      projectNode.children!.push(departmentNode);
    }

    departmentNode.total! += item.area;

    let ecosystemNode = departmentNode.children!.find((e) => e.name === item.ecosystem);

    if (!ecosystemNode) {
      ecosystemNode = { name: item.ecosystem, children: [], total: 0 };
      departmentNode.children!.push(ecosystemNode);
    }

    ecosystemNode.total! += item.area;

    let speciesNode = ecosystemNode.children!.find((s) => s.name === item.species);

    if (!speciesNode) {
      speciesNode = { name: item.species, children: [], total: 0 };
      ecosystemNode.children!.push(speciesNode);
    }

    speciesNode.total! += item.area;

    speciesNode.children!.push({ name: item.parcelname, loc: item.area });
  });

  return treeMapData;
}
