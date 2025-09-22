/*
  Warnings:

  - You are about to drop the `Constants` table. If the table is not empty, all the data it contains will be lost.
  - A unique constraint covering the columns `[name]` on the table `Project` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `name` to the `Project` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "Project_creatorId_key";

-- AlterTable
ALTER TABLE "Project" ADD COLUMN     "name" TEXT NOT NULL;

-- DropTable
DROP TABLE "Constants";

-- CreateTable
CREATE TABLE "Parcels" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "projectId" UUID NOT NULL,
    "ecosystemId" UUID NOT NULL,
    "speciesId" UUID NOT NULL,
    "area" INTEGER NOT NULL,
    "municipality" TEXT,
    "department" TEXT,
    "cadastral_id" TEXT,
    "geolocation" JSONB,
    "polygon" JSONB,

    CONSTRAINT "Parcels_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Parcels_name_key" ON "Parcels"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Parcels_projectId_key" ON "Parcels"("projectId");

-- CreateIndex
CREATE UNIQUE INDEX "Parcels_ecosystemId_key" ON "Parcels"("ecosystemId");

-- CreateIndex
CREATE UNIQUE INDEX "Parcels_speciesId_key" ON "Parcels"("speciesId");

-- CreateIndex
CREATE UNIQUE INDEX "Project_name_key" ON "Project"("name");

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_ecosystemId_fkey" FOREIGN KEY ("ecosystemId") REFERENCES "Ecosystem"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_speciesId_fkey" FOREIGN KEY ("speciesId") REFERENCES "Species"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
