# ===========================================
# Stage 1: 构建前端静态资源
# 使用国内镜像加速（DaoCloud，无需登录）
# ===========================================
FROM docker.m.daocloud.io/library/node:20-alpine AS builder

WORKDIR /app

# 依赖安装（利用 Docker 缓存层）
COPY package.json package-lock.json ./
RUN npm install --registry=https://registry.npmmirror.com

# 源码和构建配置
COPY . .

# uni-app x 要求 src/manifest.json 存在
RUN mkdir -p /app/src && cp /app/manifest.json /app/src/manifest.json

# 构建 H5 — 通过 ARG 传入后端 API 地址
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

RUN npm run build:h5

# ===========================================
# Stage 2: Nginx 运行阶段
# 用国内镜像的 nginx 减小体积
# ===========================================
FROM docker.m.daocloud.io/library/nginx:stable-alpine

COPY --from=builder /app/dist/build/h5 /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
