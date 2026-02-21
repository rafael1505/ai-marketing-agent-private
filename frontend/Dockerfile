# Further revised Dockerfile to fix permission issues with Docker build context

# Use a non-alpine Node image which has better compatibility with permissions
FROM node:20-slim AS deps

# Set up environment variables for better npm behavior
ENV npm_config_update_notifier=false
ENV npm_config_fund=false
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

# Copy only package files first to allow for better layer caching
COPY package.json package-lock.json* ./

# Clean installation approach with improved compatibility
# Install all dependencies including dev dependencies for build process
RUN npm ci --legacy-peer-deps --no-audit
# Install sharp explicitly for better image processing support in Docker
RUN npm install sharp

# Explicitly set standard permissions on all node_modules files and directories
# Added -print0 | xargs -0 for better handling of special characters in filenames
RUN find /app/node_modules -type f -print0 | xargs -0 chmod 644 || true
RUN find /app/node_modules -type d -print0 | xargs -0 chmod 755 || true
# Fix any executable files that should remain executable (like binaries)
RUN find /app/node_modules/.bin -type f -print0 | xargs -0 chmod 755 || true

# Rebuild the source code only when needed
FROM node:20-alpine AS builder
WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules
# Copy the rest of the project files
COPY . .

# Next.js collects completely anonymous telemetry data about general usage
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_URL=http://backend:8000
ENV SKIP_INVALID_PERMISSIONS=true
# Add Docker-specific environment variable to address tar issues
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Fix file permissions on source files more robustly
# Ensure all directories have correct permissions first
RUN find /app -type d -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/\.next/*" -print0 | xargs -0 -r chmod 755 || true
# Then ensure all files have correct permissions
RUN find /app -type f -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/\.next/*" -print0 | xargs -0 -r chmod 644 || true
# Make sure executables in bin directories are properly executable
RUN find /app/node_modules/.bin -type f -print0 2>/dev/null | xargs -0 -r chmod 755 || true

# Don't attempt to install @next/swc separately as it's bundled with Next.js
# Set NEXT_SHARP_PATH to avoid issues with Sharp image processing in Docker
ENV NEXT_SHARP_PATH=/app/node_modules/sharp

# Build Next.js with proper settings
# Using '--no-lint' to avoid linting issues in Docker build
# Set NODE_OPTIONS to increase memory limit for build process
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Make sure next binary is executable
RUN chmod +x ./node_modules/.bin/next

# Run the build with explicit path to make sure permissions are respected
RUN npm run build

# Production image, run the built Next.js app
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_URL=http://backend:8000
ENV SKIP_INVALID_PERMISSIONS=true

# Create non-root user for better security
RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs

# Copy build artifacts and runtime dependencies from builder
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# Final permission fix for the production environment (keep .bin executables)
RUN find /app -type d -not -path "*/.git/*" -print0 | xargs -0 -r chmod 755 || true && \
  find /app -type f -not -path "*/.git/*" -not -path "*/node_modules/.bin/*" -print0 | xargs -0 -r chmod 644 || true && \
  find /app/node_modules/.bin -type f -print0 2>/dev/null | xargs -0 -r chmod 755 || true

USER nextjs

EXPOSE 3001
ENV PORT=3001

# Start the application using Next.js built-in server (node directly avoids npm/.bin exec permission issues)
CMD ["node", "node_modules/next/dist/bin/next", "start"]
