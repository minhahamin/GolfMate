FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 5180

CMD ["npm", "run", "dev", "--", "--host"]
