/*
  Warnings:

  - Added the required column `area_factor` to the `Parcels` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Parcels" ADD COLUMN     "area_factor" INTEGER NOT NULL;
