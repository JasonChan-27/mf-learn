FROM node:18-alpine
WORKDIR /app
COPY receiver.js ./
RUN npm init -y && npm install express body-parser node-fetch
EXPOSE 9090
CMD ["node","receiver.js"]
