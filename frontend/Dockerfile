# =========================================================================
# AI Medical Scribe Platform - Frontend Service Dockerfile (Development)
# =========================================================================

FROM node:22-bookworm-slim

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install npm dependencies (using local cache workaround if needed, else standard install)
RUN npm install

# Copy application source files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Execute Vite development server
CMD ["npm", "run", "dev"]
