# Multi-stage Node.js Dockerfile (Express / Fastify / generic)
# xCloud: pair with compose-templates/nodejs-api-postgres.yml

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./
RUN if [ -f package-lock.json ]; then npm ci --omit=dev; \
    elif [ -f yarn.lock ]; then yarn --frozen-lockfile --production; \
    else npm install --omit=dev; fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodeuser && \
    chown -R nodeuser:nodejs /app
USER nodeuser

EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
