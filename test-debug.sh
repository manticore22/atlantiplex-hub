#!/usr/bin/env bash
set -euo pipefail

# Quick debug runner: validate website, signup, and payments flows
DOMAIN=${DOMAIN:-verilysovereign.org}
BASE_URL="https://${DOMAIN}"
LOGFILE="test-debug.log"

echo "=== DEBUG TEST RUN START: ${BASE_URL} ===" | tee -a "$LOGFILE"

die() { echo "ERROR: $*" >&2; exit 1; }

health_test() {
  echo "-- health check --" | tee -a "$LOGFILE"
  local paths=( "/website/health" "/studio/health" )
  for p in "${paths[@]}"; do
    url="$BASE_URL$p"
    code=$(curl -sS -o /dev/null -w "%{http_code}" "$url" || echo 0)
    echo "GET $url -> $code" | tee -a "$LOGFILE"
    if [[ "$code" != 2* && "$code" != 3* ]]; then
      die "Health endpoint failed: $url (code=$code)"
    fi
  done
}

signup_test() {
  echo "-- signup test --" | tee -a "$LOGFILE"
  TIMESTAMP=$(date +%s)
  EMAIL="dev+test-${TIMESTAMP}@example.com"
  PAYLOAD="{\"email\":\"$EMAIL\",\"password\":\"Test123!\",\"name\":\"Dev Test\"}"
  PATHS=( "/api/auth/signup" "/api/signup" )
  for p in "${PATHS[@]}"; do
    resp=$(curl -s -w "%{http_code}" -o /tmp/resp.json -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$BASE_URL$p" )
    code=$(echo "$resp" | tail -c 3)
    if [[ "$code" =~ ^[0-9]+$ ]] && [[ "$code" -ge 200 ]] && [[ "$code" -lt 300 ]]; then
      echo "Signup success via $BASE_URL$p" | tee -a "$LOGFILE"
      cat /tmp/resp.json | head -n 5 | tee -a "$LOGFILE"
      return 0
    fi
  done
  die "Signup failed on all tested endpoints"
}

stripe_test() {
  if [ -z "${STRIPE_TEST_SECRET:-}" ]; then
    echo "-- Stripe test skipped (STRIPE_TEST_SECRET not set) --" | tee -a "$LOGFILE"
    return 0
  fi
  echo "-- Stripe test --" | tee -a "$LOGFILE"

  # Create a test payment method
  METHOD_JSON=$(curl -sS -u "$STRIPE_TEST_SECRET": -d type=card \
    -d "card[number]=4242424242424242" \
    -d "card[exp_month]=12" \
    -d "card[exp_year]=2030" \
    -d "card[cvc]=123" \
    https://api.stripe.com/v1/payment_methods)
  METHOD_ID=$(echo "$METHOD_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id',''))")
  if [ -z "$METHOD_ID" ]; then
    echo "Failed to create Stripe payment method" | tee -a "$LOGFILE"; echo "$METHOD_JSON" | tee -a "$LOGFILE"; return 1
  fi
  echo "PaymentMethod=$METHOD_ID" | tee -a "$LOGFILE"

  # Create and confirm PaymentIntent
  INTENT_JSON=$(curl -sS -u "$STRIPE_TEST_SECRET": -d amount=2000 -d currency=usd -d "payment_method=$METHOD_ID" -d confirm=true -d "payment_method_types[]=card" https://api.stripe.com/v1/payment_intents)
  INTENT_ID=$(echo "$INTENT_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id',''))")
  if [ -n "$INTENT_ID" ]; then
    echo "PaymentIntent=$INTENT_ID" | tee -a "$LOGFILE"
  else
    echo "Failed to create/confirm PaymentIntent" | tee -a "$LOGFILE"; echo "$INTENT_JSON" | tee -a "$LOGFILE"; return 1
  fi
}

health_test
signup_test
stripe_test || true

echo "=== DEBUG TEST RUN DONE ===" | tee -a "$LOGFILE"
