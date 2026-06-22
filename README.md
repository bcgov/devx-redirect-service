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
podman run --rm -p 2015:2015 -p 2016:2016 -p 2017:2017 -p 2018:2018 -p 2019:2019 devx-redirect-service
```

```bash
# Docker build and run commands
docker build -t devx-redirect-service .
docker run --rm -p 2015:2015 -p 2016:2016 -p 2017:2017 -p 2018:2018 -p 2019:2019 devx-redirect-service
```

```bash
# Create python virtual environment and install requirements
cd script
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
# Run all tests against localhost
python3 test-redirects.py

# Run tests for specific port on localhost
python3 test-redirects.py --port 2015

# Run tests for specific domain (port is not applicable for domain test)
python3 test-redirects.py --host docs.developer.gov.bc.ca 
```

```bash
# Or test individual redirects manually
curl -I http://localhost:2015/sysdig-monitor-onboarding/
```


