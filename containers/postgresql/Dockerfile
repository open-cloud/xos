FROM ubuntu

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    python-software-properties \
    software-properties-common \
    postgresql-9.3 \
    postgresql-client-9.3 \
    postgresql-contrib-9.3

# Workaround for AUFS issue
# https://github.com/docker/docker/issues/783#issuecomment-56013588
RUN mkdir /etc/ssl/private-copy; mv /etc/ssl/private/* /etc/ssl/private-copy/; rm -r /etc/ssl/private; mv /etc/ssl/private-copy /etc/ssl/private; chmod -R 0700 /etc/ssl/private; chown -R postgres /etc/ssl/private

USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "ALTER USER postgres WITH SUPERUSER PASSWORD 'password' " && \
    psql --command "CREATE DATABASE xos"

# Allow remote connections. 
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf
RUN echo "host all  all    0.0.0.0/0  password" >> /etc/postgresql/9.3/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
