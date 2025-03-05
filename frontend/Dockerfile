# Stage 1: Build the React app using Node 23
FROM node:23-alpine AS build

WORKDIR /app

# Copy dependency definitions (package.json and package-lock.json if present)
COPY ./package*.json ./
RUN npm install

RUN npm install @react-oauth/google
RUN npm install jwt-decode
# Copy the rest of the source code and build production version
COPY . .
RUN npm run build --verbose


# Stage 2: Serve the built app with NGINX
FROM nginx:stable-alpine

# Remove default NGINX static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the production build from the previous stage into NGINX's directory
COPY --from=build /app/build /usr/share/nginx/html

# Copy NGINX configuration file
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 and start NGINX
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
