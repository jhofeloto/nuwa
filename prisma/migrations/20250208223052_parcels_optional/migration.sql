-- DropForeignKey
ALTER TABLE "Parcels" DROP CONSTRAINT "Parcels_ecosystemId_fkey";

-- DropForeignKey
ALTER TABLE "Parcels" DROP CONSTRAINT "Parcels_projectId_fkey";

-- DropForeignKey
ALTER TABLE "Parcels" DROP CONSTRAINT "Parcels_speciesId_fkey";

-- AlterTable
ALTER TABLE "Parcels" ALTER COLUMN "projectId" DROP NOT NULL,
ALTER COLUMN "ecosystemId" DROP NOT NULL,
ALTER COLUMN "speciesId" DROP NOT NULL;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_ecosystemId_fkey" FOREIGN KEY ("ecosystemId") REFERENCES "Ecosystem"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_speciesId_fkey" FOREIGN KEY ("speciesId") REFERENCES "Species"("id") ON DELETE SET NULL ON UPDATE CASCADE;
