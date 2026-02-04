FROM node:20-alpine AS builder
WORKDIR /app
COPY web/stage/package.json ./
RUN npm install --silent
COPY web/stage/ .
RUN echo "Stage build complete (no frontend assets)" 
EXPOSE 9001
CMD ["node", "server.js"]
