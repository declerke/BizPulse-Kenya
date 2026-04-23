#!/bin/sh
set -e

cd /app
rm -rf .evidence

# Retry npm install up to 3 times on network failure
for i in 1 2 3; do
  npm install --legacy-peer-deps --no-fund --no-audit && break
  echo "npm install attempt $i failed, retrying in 15s..."
  sleep 15
done

mkdir -p sources/snowflake
printf "name: snowflake\ntype: snowflake\noptions:\n  account: %s\n  username: %s\n  password: %s\n  database: %s\n  warehouse: %s\n  schema: MART\n  role: %s\n" \
  "$SNOWFLAKE_ACCOUNT" "$SNOWFLAKE_USER" "$SNOWFLAKE_PASSWORD" \
  "$SNOWFLAKE_DATABASE" "$SNOWFLAKE_WAREHOUSE" "$SNOWFLAKE_ROLE" \
  > sources/snowflake/connection.yaml

# Patch Evidence template to exclude core-components from esbuild optimization
# Without this, esbuild crashes preprocessing the .svelte files inside core-components
sed -i "s/exclude: \['svelte-icons'/exclude: ['@evidence-dev\/core-components', 'svelte-icons'/" \
  /app/node_modules/@evidence-dev/evidence/template/vite.config.js

# Place a minimal postcss config inside core-components so svelte-preprocess finds it
# when transforming .svelte files in that package. postcss-load-config searches up from
# the file path and stops at package boundaries — it never reaches /app/.
printf 'module.exports = { plugins: [] };\n' \
  > /app/node_modules/@evidence-dev/core-components/postcss.config.cjs

npm run sources
npm run build
exec npx serve build -p 3000 --no-clipboard
