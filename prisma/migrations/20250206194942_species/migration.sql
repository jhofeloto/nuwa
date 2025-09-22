-- AlterTable
ALTER TABLE "Project" ALTER COLUMN "country" DROP NOT NULL,
ALTER COLUMN "department" DROP NOT NULL;

-- CreateTable
CREATE TABLE "Constants" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "value" DOUBLE PRECISION NOT NULL,
    "unit" TEXT NOT NULL,

    CONSTRAINT "Constants_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MathModels" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,

    CONSTRAINT "MathModels_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Species" (
    "id" UUID NOT NULL,
    "common_name" TEXT NOT NULL,
    "scientific_name" TEXT NOT NULL,
    "family" TEXT NOT NULL,
    "functional_type" TEXT NOT NULL,
    "values" JSONB NOT NULL,
    "comments" TEXT,

    CONSTRAINT "Species_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Constants_name_key" ON "Constants"("name");

-- CreateIndex
CREATE UNIQUE INDEX "MathModels_name_key" ON "MathModels"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Species_common_name_key" ON "Species"("common_name");

-- CreateIndex
CREATE UNIQUE INDEX "Species_scientific_name_key" ON "Species"("scientific_name");
