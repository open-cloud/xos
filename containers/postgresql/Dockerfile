FROM ubuntu

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    python-software-properties \
    software-properties-common \
    postgresql-9.3 \
    postgresql-client-9.3 \
    postgresql-contrib-9.3

USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "ALTER USER postgres WITH SUPERUSER PASSWORD 'password';"

# Allow remote connections. 
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
