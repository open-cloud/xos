# xosproject/xos-postgres
FROM ubuntu:14.04.5

# Version of PostgreSQL to install
ENV PGSQL_VERSION 9.6

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    python-software-properties \
    software-properties-common \
    postgresql-$PGSQL_VERSION \
    postgresql-client-$PGSQL_VERSION \
    postgresql-contrib-$PGSQL_VERSION \
 && rm -rf /var/lib/apt/lists/*

# Workaround for AUFS issue
# https://github.com/docker/docker/issues/783#issuecomment-56013588
RUN mkdir /etc/ssl/private-copy; mv /etc/ssl/private/* /etc/ssl/private-copy/; rm -r /etc/ssl/private; mv /etc/ssl/private-copy /etc/ssl/private; chmod -R 0700 /etc/ssl/private; chown -R postgres /etc/ssl/private

USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "ALTER USER postgres WITH SUPERUSER PASSWORD 'password' " && \
    psql --command "CREATE DATABASE xos"

# Allow remote connections.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/$PGSQL_VERSION/main/pg_hba.conf
RUN echo "host all  all    0.0.0.0/0  password" >> /etc/postgresql/$PGSQL_VERSION/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/$PGSQL_VERSION/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Label image
ARG org_label_schema_schema_version=1.0
ARG org_label_schema_name=xos-postgres
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown

LABEL org.label-schema.schema-version=$org_label_schema_schema_version \
      org.label-schema.name=$org_label_schema_name \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date

CMD ["/usr/lib/postgresql/$PGSQL_VERSION/bin/postgres", "-D", "/var/lib/postgresql/$PGSQL_VERSION/main", "-c", "config_file=/etc/postgresql/$PGSQL_VERSION/main/postgresql.conf"]
