FROM node:20-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM node:20-slim AS run
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
# Shell form so ${PORT} is expanded at container start (Render injects PORT
# and requires binding to it; local docker-compose has no PORT set, so this
# falls back to 3000 to match the compose port mapping).
CMD npm run start -- -p ${PORT:-3000}
