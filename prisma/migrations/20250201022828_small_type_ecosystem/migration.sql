/*
  Warnings:

  - You are about to drop the column `Type` on the `Ecosystem` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[type]` on the table `Ecosystem` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `type` to the `Ecosystem` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "Ecosystem_Type_key";

-- AlterTable
ALTER TABLE "Ecosystem" DROP COLUMN "Type",
ADD COLUMN     "type" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "Ecosystem_type_key" ON "Ecosystem"("type");
