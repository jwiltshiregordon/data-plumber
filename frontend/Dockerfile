FROM nginx:1.21

COPY ./dist /var/www/static/frontend
COPY ./staticfiles /var/www/static/backend
COPY ./pyodide var/www/static/pyodide
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
