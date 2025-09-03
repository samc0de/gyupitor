# Use the official Nginx image from Docker Hub
FROM nginx:alpine

# Remove the default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the static assets from the implementation directory to the Nginx html directory
COPY implementation/index.html /usr/share/nginx/html/

# Expose port 80 to the outside world
EXPOSE 80

# Command to run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]