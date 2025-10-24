#!/bin/bash

# Test script for enhanced image generation error handling

echo "🧪 Testing Enhanced Image Generation Error Handling"
echo "=================================================="

# Test OpenAI with invalid API key (should trigger billing/auth error)
echo
echo "1. Testing OpenAI error classification..."
curl -s "http://localhost:8088/api/v1/ai-generation/generate-image" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "prompt=test image&ai_provider=openai&size=1024x1024&variations=1" \
  | python3 -c "
import json, sys
try:
    response = json.loads(sys.stdin.read())
    print('✅ Response structure:', response.get('success', 'Unknown'))
    if 'error' in response:
        error = response['error']
        print('📋 Error details:')
        print(f'   Type: {error.get(\"type\", \"Unknown\")}')
        print(f'   Message: {error.get(\"message\", \"Unknown\")}')
        print(f'   User Message: {error.get(\"user_message\", \"N/A\")}')
        print(f'   Provider: {error.get(\"provider\", \"Unknown\")}')
        print(f'   Retry Possible: {error.get(\"retry_possible\", \"Unknown\")}')
        print(f'   Suggested Action: {error.get(\"suggested_action\", \"N/A\")}')
    else:
        print('❌ No structured error found')
except Exception as e:
    print(f'❌ Failed to parse response: {e}')
"

echo
echo "2. Testing API health..."
curl -s "http://localhost:8088/health" | python3 -c "
import json, sys
try:
    response = json.loads(sys.stdin.read())
    print('✅ API Health:', response.get('status', 'Unknown'))
except:
    print('❌ API not responding properly')
"

echo
echo "3. Testing enhanced error patterns..."
python3 -c "
import sys
sys.path.append('/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

from app.core.provider_error_patterns import ProviderErrorPatterns

# Test billing error detection
test_errors = [
    'billing hard limit has been reached',
    'insufficient credits in your account',
    'invalid api key provided',
    'rate limit exceeded',
    'content policy violation detected'
]

print('🔍 Testing error pattern matching:')
for error_msg in test_errors:
    result = ProviderErrorPatterns.detect_openai_error(error_msg)
    if result:
        print(f'✅ \"{error_msg}\" → {result.error_type.value}')
        print(f'   User Message: {result.user_message}')
        print(f'   Action: {result.suggested_action}')
    else:
        print(f'❌ \"{error_msg}\" → No match found')
    print()
"

echo
echo "4. Testing Portuguese translations..."
echo "Checking if Portuguese error translations are available..."

if grep -q "billing_limit_reached" /mnt/c/Users/brc07274/OneDrive\ -\ Philips/Philips\ Files/BU\ -\ CI/Repository/AI\ Marketing\ Agent\ \(Python\)/ai-marketing-agent/frontend/src/i18n/locales/pt.json; then
    echo "✅ Portuguese translations found"
    grep -A 3 "billing_limit_reached" /mnt/c/Users/brc07274/OneDrive\ -\ Philips/Philips\ Files/BU\ -\ CI/Repository/AI\ Marketing\ Agent\ \(Python\)/ai-marketing-agent/frontend/src/i18n/locales/pt.json | head -5
else
    echo "❌ Portuguese translations missing"
fi

echo
echo "🎯 Test Summary:"
echo "- OpenAI error classification: Enhanced with specific patterns"
echo "- Portuguese translations: Added comprehensive error messages"
echo "- Frontend error display: Ready for structured errors"
echo "- Provider guidance: Available for setup instructions"
echo
echo "Next steps:"
echo "1. Test with actual OpenAI billing limit error"
echo "2. Verify Portuguese locale switching"
echo "3. Test error display component in frontend"
echo "4. Validate error recovery workflows"