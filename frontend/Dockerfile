FROM node:26-alpine AS build
RUN npm install -g corepack && corepack enable
WORKDIR /web
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build && cp -r node_modules/@excalidraw/excalidraw/dist/prod/fonts dist/fonts

FROM nginx:1.31-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
