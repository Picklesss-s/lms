FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# Required for Vite to bind to all interfaces in Docker
CMD ["npm", "run", "dev", "--", "--host"]
