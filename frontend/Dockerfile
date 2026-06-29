# =========================================================================
# AI Medical Scribe Platform - Frontend Service Dockerfile (Development)
# =========================================================================

FROM node:20-bookworm-slim

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install npm dependencies 
RUN npm install --include=optional

# Copy application source files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Execute Vite development server
CMD ["npm", "run", "dev", "--", "--host"]