# 프로덕션 전용 이미지 (Railway 등 배포용 기본 Dockerfile).
# 로컬 개발(docker-compose)은 Vite dev server를 쓰는 Dockerfile.dev를 명시적으로 사용한다.
# 여기서는 정적 빌드 후 nginx로 서빙한다.
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Vite는 빌드 시점에 환경변수를 JS 번들에 굽는다. Railway가 서비스 변수로 넣어준
# VITE_API_BASE_URL이 build-arg로도 전달되도록 ARG/ENV로 받아준다.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
