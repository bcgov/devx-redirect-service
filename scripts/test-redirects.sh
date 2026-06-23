#!/usr/bin/env bash
# Test script for redirect functionality

set -euo pipefail

DOCS_URL="http://localhost:2015/"
SO_URL="http://localhost:2017/"
RC_URL="http://localhost:2018/"
JA_URL="http://localhost:2019/"

test_url() {
    local url_to_test="$1"
    local expected_url="$2"
    local response status location
    
    response=$(curl -s -w "%{http_code}\n%{redirect_url}\n" "$url_to_test")
    status="$(printf '%s' "$response" | tail -n 2 | head -n 1)"
    location="$(printf '%s' "$response" | tail -n 1)"

    if [[ "$status" == "301" && "$location" == "$expected_url" ]]; then
        echo "   ✅ OK - $location"
    else
        echo "   ❌ FAIL - $location (Status=$status)" >&2
        exit 1
    fi
}

check_error_response() {
    local url_to_test="$1"
    response=$(curl -s -o /dev/null -w "%{http_code}\n" "${url_to_test}non-existent-path/")
    status="$response"

    if [[ "$status" == "404" ]]; then
      echo "   ✅ 404 handling OK"
    else
      echo "   ❌ Expected 404 but got $status" >&2
      exit 1
    fi
}

echo "Testing $DOCS_URL redirects"
test_url "$DOCS_URL/" "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/"
test_url "$DOCS_URL/sysdig-monitor-onboarding/" "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/docs/app-monitoring/sysdig-monitor-onboarding/"
test_url "$DOCS_URL/rocketchat-etiquette/" "https://developer.gov.bc.ca/docs/default/component/bc-developer-guide/rocketchat/rocketchat-etiquette/"
test_url "$DOCS_URL/platform-security-tools/" "https://developer.gov.bc.ca/docs/default/component/platform-developer-docs/docs/security-and-privacy-compliance/platform-security-tools/"

echo "Testing $DOCS_URL 404 handling"
check_error_response $DOCS_URL

echo "Testing $SO_URL redirects"
test_url "$SO_URL/" "https://github.com/bcgov/bcgov-community-discussions/discussions"
test_url "$SO_URL/questions" "https://github.com/bcgov/bcgov-community-discussions/discussions"
test_url "$SO_URL/questions/94/117" "https://github.com/bcgov/bcgov-community-discussions/discussions/16#discussioncomment-14942167"
test_url "$SO_URL/q/100" "https://github.com/bcgov/bcgov-community-discussions/discussions/18"
test_url "$SO_URL/a/121" "https://github.com/bcgov/bcgov-community-discussions/discussions/21#discussioncomment-14942197"

echo "Testing $SO_URL 404 handling"
check_error_response $SO_URL

echo "Testing $RC_URL redirects"
test_url "$RC_URL/" "https://bcgov.sharepoint.com/teams/developercommunity"
test_url "$RC_URL/some/path?test=1" "https://bcgov.sharepoint.com/teams/developercommunity"

echo "Testing $JA_URL redirects"
test_url "$JA_URL/" "https://developer.gov.bc.ca/docs/default/component/bc-developer-guide/use-github-in-bcgov/bc-government-organizations-in-github/#single-sign-on"
test_url "$JA_URL/some/other/path?foo=bar" "https://developer.gov.bc.ca/docs/default/component/bc-developer-guide/use-github-in-bcgov/bc-government-organizations-in-github/#single-sign-on"
