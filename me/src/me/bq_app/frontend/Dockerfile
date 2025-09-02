FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY index.html .
COPY script.js .

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]