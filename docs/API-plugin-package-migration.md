# Migration setup for plugin packages

## Preface
This guide is to help with local development of migrations in plugin packages and testing. It starts with instructions to check migration status and run the same.

## Checking migration status

### 1. CLI
As a prerequisite, have Node 14.17.5 installed. 
Follow [these](https://github.com/reactioncommerce/api-migrations#local-development-usage) steps to set up the api-migrations repo.
When you run the `MONGO_URL=mongodb://localhost:27017/reaction npx migrator migrate` command it will indicate via a table if any migration should be run.  It prompts a question (y/n) to the user to start the migration.

### 2. Reaction-api logs
Starting the app automatically checks if the latest versions are running. Check reaction logs using `docker-compose logs -f api`.


## Setting up a new migration track
You can look at the [simple-authorization](https://github.com/reactioncommerce/plugin-simple-authorization) plugin code for an example to follow.
To add a migration to an API plugin package, follow the below steps:

1. In the plugin package create a `migrations` folder alongside the `src` folder.
2. Create `migrationsNamespace.js` and add the line `export const migrationsNamespace = "<package-name>";`.
3. Create `<n>.js` which will house the `up()` and `down()`. The `up` and `down` functions should do whatever they need to do to move data from your N-1 or N+1 schema to your N schema. Both types of functions receive a migration context, which has a connection to the MongoDB database and a progress function for reporting progress. For more information on naming convention go here
4. Create `index.js` which exports the namespace and migration script.
5. Add `export { default as migrations } from "./migrations/index.js";` in your plugin entry point file i.e, `<api-plugin-package>/index.js`.
6. Add the latest version of the `@reactioncommerce/db-version-check` NPM package as a dependency using `npm install @reactioncommerce/db-version-check@latest`.
7. Add and register a `preStartup` function in `src/index.js`. In it, call `doesDatabaseVersionMatch` to prevent API startup if the data isn't compatible with the code. The preStartup.js is responsible for identifying version mismatch. It throws an error if a migration is required and prevents api from running.

### In api-migrations
1. Add the new track to `api-migrations/migrator.config.js` following the existing syntax. The app looks at this file to pick the desired version and checks against the migrations table in the DB to identify the current version.
2. Install the plugin package using `npm install @reactioncommerce/<api-plugin-package>


## Testing for local development
1. Copy (replace if necessary) the entire api plugin package with the new migration code into `api-migrations/node_modules/@reactioncommerce`. 
2. Run `MONGO_URL=mongodb://localhost:27017/reaction npx migrator migrate`
3. Verify if the changes take effect.
4. Once you have a successful test run, a re-run will show that all migrations are at the desired version. To revert the migration, change back to the previous version in `api-migrations/migrator.config.js` and run the same migrate command. If it is a new track then delete the migration entry in the `migrations` table in the database.
