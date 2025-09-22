-- CreateEnum
CREATE TYPE "Role" AS ENUM ('GESTOR', 'ADMIN');

-- CreateEnum
CREATE TYPE "Status" AS ENUM ('Seed', 'InProgress', 'Finished', 'Canceled');

-- CreateTable
CREATE TABLE "Ecosystem" (
    "id" SERIAL NOT NULL,
    "Type" TEXT NOT NULL,
    "description" TEXT,
    "values" JSONB NOT NULL,

    CONSTRAINT "Ecosystem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Keyword" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,

    CONSTRAINT "Keyword_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "User" (
    "id" SERIAL NOT NULL,
    "name" TEXT,
    "email" TEXT NOT NULL,
    "role" "Role" NOT NULL DEFAULT 'GESTOR',

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Project" (
    "id" UUID NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "abstract" TEXT,
    "country" VARCHAR(255) NOT NULL,
    "status" "Status" NOT NULL DEFAULT 'Seed',
    "department" VARCHAR(255) NOT NULL,
    "creatorId" INTEGER NOT NULL,
    "values" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Project_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ProjectKeyword" (
    "projectId" UUID NOT NULL,
    "keywordId" UUID NOT NULL,

    CONSTRAINT "ProjectKeyword_pkey" PRIMARY KEY ("projectId","keywordId")
);

-- CreateIndex
CREATE UNIQUE INDEX "Ecosystem_Type_key" ON "Ecosystem"("Type");

-- CreateIndex
CREATE UNIQUE INDEX "Keyword_name_key" ON "Keyword"("name");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- AddForeignKey
ALTER TABLE "Project" ADD CONSTRAINT "Project_creatorId_fkey" FOREIGN KEY ("creatorId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProjectKeyword" ADD CONSTRAINT "ProjectKeyword_keywordId_fkey" FOREIGN KEY ("keywordId") REFERENCES "Keyword"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProjectKeyword" ADD CONSTRAINT "ProjectKeyword_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "Project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
