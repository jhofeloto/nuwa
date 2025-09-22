/*
  Warnings:

  - You are about to alter the column `area` on the `Parcels` table. The data in that column could be lost. The data in that column will be cast from `Integer` to `Decimal(10,7)`.
  - Made the column `speciesId` on table `Parcels` required. This step will fail if there are existing NULL values in that column.
  - Added the required column `updatedAt` to the `User` table without a default value. This is not possible if the table is not empty.

*/
-- CreateEnum
CREATE TYPE "Index" AS ENUM ('NDVI', 'NDWI', 'SAVI', 'OSAVI');

-- CreateEnum
CREATE TYPE "AnalysisType" AS ENUM ('MANUAL', 'ML');

-- DropForeignKey
ALTER TABLE "Parcels" DROP CONSTRAINT "Parcels_speciesId_fkey";

-- DropForeignKey
ALTER TABLE "Project" DROP CONSTRAINT "Project_creatorId_fkey";

-- AlterTable
ALTER TABLE "Parcels" ALTER COLUMN "speciesId" SET NOT NULL,
ALTER COLUMN "area" DROP NOT NULL,
ALTER COLUMN "area" SET DATA TYPE DECIMAL(10,7),
ALTER COLUMN "area_factor" SET DEFAULT 0;

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "emailVerified" TIMESTAMP(3),
ADD COLUMN     "updatedAt" TIMESTAMP(3) NOT NULL;

-- CreateTable
CREATE TABLE "Account" (
    "userId" UUID NOT NULL,
    "type" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "providerAccountId" TEXT NOT NULL,
    "refresh_token" TEXT,
    "access_token" TEXT,
    "expires_at" INTEGER,
    "token_type" TEXT,
    "scope" TEXT,
    "id_token" TEXT,
    "session_state" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Account_pkey" PRIMARY KEY ("provider","providerAccountId")
);

-- CreateTable
CREATE TABLE "Session" (
    "sessionToken" TEXT NOT NULL,
    "userId" UUID NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL
);

-- CreateTable
CREATE TABLE "VerificationToken" (
    "identifier" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "VerificationToken_pkey" PRIMARY KEY ("identifier","token")
);

-- CreateTable
CREATE TABLE "Coverage" (
    "id" UUID NOT NULL,
    "ecosystemId" UUID,
    "description" TEXT,
    "type" TEXT,
    "index" "Index" NOT NULL DEFAULT 'NDVI',
    "values" JSONB NOT NULL,

    CONSTRAINT "Coverage_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ParcelAnalysis" (
    "id" UUID NOT NULL,
    "parcelId" UUID NOT NULL,
    "analysisType" "AnalysisType" NOT NULL DEFAULT 'ML',
    "values" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ParcelAnalysis_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Contracts" (
    "contractId" TEXT NOT NULL,
    "projectId" UUID,
    "contractName" TEXT NOT NULL,
    "contractType" TEXT NOT NULL,
    "contractAddress" TEXT,
    "compiledCode" JSONB NOT NULL,
    "tokenName" TEXT,
    "lockTxHash" TEXT,
    "active" BOOLEAN NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Contracts_pkey" PRIMARY KEY ("contractId")
);

-- CreateTable
CREATE TABLE "Transactions" (
    "transactionId" TEXT NOT NULL,
    "contractId" TEXT,
    "from" TEXT NOT NULL,
    "to" TEXT NOT NULL,
    "value" BIGINT NOT NULL,
    "assets" JSONB,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "lockedInContract" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "Transactions_pkey" PRIMARY KEY ("transactionId")
);

-- CreateIndex
CREATE UNIQUE INDEX "Session_sessionToken_key" ON "Session"("sessionToken");

-- CreateIndex
CREATE UNIQUE INDEX "Contracts_contractId_key" ON "Contracts"("contractId");

-- CreateIndex
CREATE UNIQUE INDEX "Transactions_transactionId_key" ON "Transactions"("transactionId");

-- AddForeignKey
ALTER TABLE "Account" ADD CONSTRAINT "Account_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Project" ADD CONSTRAINT "Project_creatorId_fkey" FOREIGN KEY ("creatorId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Parcels" ADD CONSTRAINT "Parcels_speciesId_fkey" FOREIGN KEY ("speciesId") REFERENCES "Species"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Coverage" ADD CONSTRAINT "Coverage_ecosystemId_fkey" FOREIGN KEY ("ecosystemId") REFERENCES "Ecosystem"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ParcelAnalysis" ADD CONSTRAINT "ParcelAnalysis_parcelId_fkey" FOREIGN KEY ("parcelId") REFERENCES "Parcels"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Contracts" ADD CONSTRAINT "Contracts_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Transactions" ADD CONSTRAINT "Transactions_contractId_fkey" FOREIGN KEY ("contractId") REFERENCES "Contracts"("contractId") ON DELETE CASCADE ON UPDATE CASCADE;
