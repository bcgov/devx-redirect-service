FROM caddy:2.11.4-alpine@sha256:77c07d5ebfa5be9fd6c820d2094ae662c9e7eeb9bf98346b7f639900263ee2a2

# Needed to use Caddy's logging format transform
RUN caddy add-package github.com/caddyserver/transform-encoder   

# From https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/images/creating-images#use-uid_create-images
# Even though the admin and persistent config is turned off in the Caddyfile, caddy still creates files
# in the data directory. So give it the appropriate permissions.
RUN mkdir -p /data/caddy && \
    chgrp -R 0 /data && \
    chmod -R g=u /data

WORKDIR /srv

COPY Caddyfile /etc/caddy/Caddyfile
RUN caddy fmt --overwrite /etc/caddy/Caddyfile

COPY error.html error_so.html /srv/

EXPOSE 2015 2016 2017 2018 2019

USER 1001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=5 CMD wget -qO- http://localhost:2016/health || exit 1

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
