# devx-redirect-service

This project redirects legacy URLs managed by the Developer Experience Team. 

The [Caddyfile](./Caddyfile) contains the list of redirected URLs.

## About

The project uses:
- Dockerfile with Caddy web server
- Caddyfile configuration for redirects 
- CI workflow for automated testing

## Testing

The `test-redirects.py` script tests a subset of redirects and the error page.

It tests against localhost.

Test cases are defined in YAML test-cases.yaml file. 

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
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
# Run all tests against 
python3 test-redirects.py 

# Run tests for a specific service
python3 test-redirects.py --service just-ask
```

Refer to the test-cases.yaml file to get the service names.

```bash
# Or test individual redirects manually
curl -I http://localhost:2015/sysdig-monitor-onboarding/
```

### Adding a new test case

Add new test cases to the test-cases.yaml file. No code changes should be required.


