FROM nginx:1.21

RUN apt-get update && \
    apt-get install -y wget bzip2

RUN mkdir -p /var/www/static/pyodide && \
    wget https://github.com/pyodide/pyodide/releases/download/0.23.4/pyodide-0.23.4.tar.bz2 && \
    tar -xjf pyodide-0.23.4.tar.bz2 -C /var/www/static/pyodide --strip-components=1 && \
    rm pyodide-0.23.4.tar.bz2

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
