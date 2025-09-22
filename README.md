# Nuwa

Token Impact System for Ecosystem Conservation



### Instructions to initialize

#### Reseting the database or running the app for the first time

1. Use prisma to migrate the schema and apply all the scripts that are run in the database

These commands reset the database (delete all the records) and create the migrations again including the functions and store procedures. Make sure you have the excel file as a backup for the projects that you want to recreate.

```bash
npx prisma migrate reset
npx prisma generate
npx prisma migrate dev
```

2. Run the init database page to create dummy user

[Seed Database](http://localhost:3000/seed)

3. Populate the database with the upload option in the menu bar

Upload data at least for one project to create records and to create first materialized views associated to the project.







