/*
  Warnings:

  - You are about to drop the column `abstract` on the `Project` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Project" DROP COLUMN "abstract",
ADD COLUMN     "description" TEXT;
