FROM node:20

WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./

RUN npm install

# Copy the rest of the app
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
