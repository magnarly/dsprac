# Frontend Dockerfile - Next.js
FROM node:20-alpine

WORKDIR /workspace

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy rest of the application
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]
