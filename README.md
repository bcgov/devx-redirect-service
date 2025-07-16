# platform-developer-docs-redirect

This project is a redirect service using Caddy to redirect legacy URLs to the new [platform-developer-docs](https://github.com/bcgov/platform-developer-docs) location.

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
podman build -t platform-docs-redirect-test .
podman run --rm -p 2015:2015 -p 2016:2016 -p 2017:2017 platform-docs-redirect-test
```

```bash
# Docker build and run commands
docker build -t platform-docs-redirect-test .
docker run --rm -p 2015:2015 -p 2016:2016 -p 2017:2017 platform-docs-redirect-test
```

```bash
# Run the automated tests
./scripts/test-redirects.sh localhost 2015

# Or test individual redirects manually
curl -I http://localhost:2015/sysdig-monitor-onboarding/
```


