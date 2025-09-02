# Use a lightweight Nginx image
FROM nginx:1.21-alpine

# Copy static assets
COPY index.html /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]