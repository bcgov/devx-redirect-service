#!/usr/bin/env bash
# Test script for redirect functionality
# Can be run locally or from CI/CD pipeline

set -euo pipefail

HOST=${1:-localhost}
PORT1=${2:-2015}
PORT2=${3:-2017}

paths_port1=(
  "/"
  "/sysdig-monitor-onboarding/"
  "/rocketchat-etiquette/"
  "/platform-security-tools/"
)

expected_destinations_port1=(
  "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/"
  "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/docs/app-monitoring/sysdig-monitor-onboarding/"
  "https://developer.gov.bc.ca/docs/default/component/bc-developer-guide/rocketchat/rocketchat-etiquette/"
  "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/docs/security-and-privacy-compliance/platform-security-tools/"
)

paths_port2=(
  "/"
  "/questions"
  "/questions/94/117"
  "/q/100"
  "/a/121"
)

expected_destinations_port2=(
  "https://github.com/bcgov/bcgov-community-discussions/discussions"
  "https://github.com/bcgov/bcgov-community-discussions/discussions"
  "https://github.com/bcgov/bcgov-community-discussions/discussions/16#discussioncomment-14942167"
  "https://github.com/bcgov/bcgov-community-discussions/discussions/18"
  "https://github.com/bcgov/bcgov-community-discussions/discussions/21#discussioncomment-14942197"
)


run_tests() {
  local paths_array_name="$1"
  local expected_array_name="$2"
  local port="$3"

  local length
  eval "length=\${#${paths_array_name}[@]}"

  for ((i=0; i<length; i++)); do
    eval "path=\${${paths_array_name}[i]}"
    eval "expected=\${${expected_array_name}[i]}"

    echo "🔎 Testing $path"
    echo "   ↳ Expect: $expected"

    response=$(curl -s -w "%{http_code}\n%{redirect_url}\n" "http://$HOST:$port$path")
    status=$(echo "$response" | head -1)
    location=$(echo "$response" | tail -1)

    if [[ "$status" == "301" && "$location" == "$expected" ]]; then
      echo "   ✅ OK"
    else
      echo "   ❌ FAIL: Status=$status, Location=$location"
      exit 1
    fi
  done

  # 404 test
  echo "🔎 Testing error handling (/non-existent-path/)"
  response=$(curl -s -o /dev/null -w "%{http_code}\n" "http://$HOST:$port/non-existent-path/")
  status="$response"

  if [[ "$status" == "404" ]]; then
    echo "   ✅ 404 handling OK"
  else
    echo "   ❌ Expected 404 but got $status"
    exit 1
  fi
}


echo "🧪 Testing redirects on $HOST:$PORT1"
run_tests paths_port1 expected_destinations_port1 "$PORT1"

echo "🧪 Testing redirects on $HOST:$PORT2"
run_tests paths_port2 expected_destinations_port2 "$PORT2"

echo "🎉 All tests passed successfully!"
