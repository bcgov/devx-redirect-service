FROM caddy:2.10-alpine@sha256:953131cfea8e12bfe1c631a36308e9660e4389f0c3dfb3be957044d3ac92d446

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

COPY error.html /srv/error.html

EXPOSE 2015 2016 2017

USER 1001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=5 CMD wget -qO- http://localhost:2016/health || exit 1

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
