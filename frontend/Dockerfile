FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN mkdir -p public && npm run build

# Production image, copy all files and run next
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

COPY package*.json ./

RUN npm ci --only=production && mkdir -p public

COPY --from=builder /app/.next ./.next
RUN ls /app/public
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

EXPOSE 3000

CMD ["npm", "start"]