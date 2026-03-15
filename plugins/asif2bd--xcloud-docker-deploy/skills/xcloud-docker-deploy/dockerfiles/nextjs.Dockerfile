# Next.js Dockerfile — standalone output mode
# REQUIRED: next.config.js must have output: 'standalone'
# xCloud: pair with compose-templates/nextjs-postgres.yml

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci; \
    elif [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    else npm install; fi

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
