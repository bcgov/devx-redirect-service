# devx-redirect-service

This project redirects legacy URLs managed by the Developer Experience Team. 

The [Caddyfile](./Caddyfile) contains the list of redirected URLs.

## About

The project uses:
- Dockerfile with Caddy web server
- Caddyfile configuration for redirects 
- CI workflow for automated testing

## Testing

The `test-redirects.sh` script tests a subset of redirects and the error page.

You can run it locally using Docker or Podman.

```bash
# Podman build and run commands
podman build -t devx-redirect-service .
podman run --rm -p 2015:2015 -p 2016:2016 devx-redirect-service
```

```bash
# Docker build and run commands
docker build -t devx-redirect-service .
docker run --rm -p 2015:2015 -p 2016:2016 devx-redirect-service
```

```bash
# Run the automated tests
./scripts/test-redirects.sh localhost 2015

# Or test individual redirects manually
curl -I http://localhost:2015/sysdig-monitor-onboarding/
```


