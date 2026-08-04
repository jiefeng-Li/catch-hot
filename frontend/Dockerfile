# ---------- 构建阶段 ----------
FROM node:20-alpine AS build

WORKDIR /app

# 先复制依赖清单，充分利用 Docker 层缓存
COPY package.json package-lock.json ./
RUN npm ci

# 复制源码并构建
COPY index.html vite.config.js ./
COPY src ./src

# 构建期注入后端 API 地址，对应 src/api.js 中的 import.meta.env.VITE_API_BASE_URL
# 生产环境使用同源 /api，由 nginx 转发到后端内网域名；不要在这里写后端公网/内网地址
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ---------- 运行阶段 ----------
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
