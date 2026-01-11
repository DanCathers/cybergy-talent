# =========================================================================
# Frontend Dockerfile — Cybergy Talent Next.js app
# Multi-stage build: install + build in one stage, run a lean image in the next.
# Runs as a NON-ROOT user for security.
# =========================================================================

# ---- Stage 1: build ----
FROM node:20-alpine AS builder
WORKDIR /app

# Install dependencies using the lockfile for reproducible builds.
COPY package.json package-lock.json* ./
RUN npm ci

# Copy the source and produce an optimized production build.
COPY . .
RUN npm run build

# ---- Stage 2: runtime ----
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Create and switch to a non-root user.
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy only what's needed to run the built app.
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

USER nextjs

EXPOSE 3000

CMD ["npm", "run", "start"]
