FROM node:26-alpine AS build
RUN npm install -g corepack@0.36.0 && corepack enable
WORKDIR /web
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:1.31-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
