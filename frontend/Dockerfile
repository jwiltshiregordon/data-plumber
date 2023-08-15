FROM nginx:1.21

# Install wget
RUN apt-get update && \
    apt-get install -y wget

# Download, extract, and remove Pyodide
RUN wget https://github.com/pyodide/pyodide/releases/download/0.23.4/pyodide-0.23.4.tar.bz2 && \
    tar -xjf pyodide-0.23.4.tar.bz2 -C /var/www/static/pyodide --strip-components=1 && \
    rm pyodide-0.23.4.tar.bz2

# Copy the remaining necessary files
COPY ./dist /var/www/static/frontend
COPY ./staticfiles /var/www/static/backend
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
