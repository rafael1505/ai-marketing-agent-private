#!/bin/bash

# Simple test to check frontend-backend connectivity

echo "=== Testing Frontend-Backend Connection ==="
echo ""

# Test 1: Direct API call (should work without auth for ai-providers)
echo "1. Testing direct API call to ai-providers endpoint..."
RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" http://localhost:8088/api/v1/ai-providers)
HTTP_CODE=$(echo "$RESPONSE" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed 's/HTTP_CODE:[0-9]*$//')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Direct API call successful (HTTP $HTTP_CODE)"
    PROVIDER_COUNT=$(echo "$BODY" | grep -o '"name"' | wc -l)
    echo "  Found $PROVIDER_COUNT providers"
    
    # Check for pricing data
    if echo "$BODY" | grep -q '"pricing"'; then
        echo "✓ Pricing data present in response"
        echo "$BODY" | grep -o '"tier":"[^"]*"' | head -3 | sed 's/"tier":"/ - Tier: /' | sed 's/"$//'
    else
        echo "✗ No pricing data found"
    fi
else
    echo "✗ Direct API call failed (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
fi

echo ""

# Test 2: Check if frontend can make CORS requests to backend
echo "2. Testing CORS from frontend to backend..."
CORS_TEST=$(curl -s -X OPTIONS -H "Origin: http://localhost:3001" \
                 -H "Access-Control-Request-Method: GET" \
                 -H "Access-Control-Request-Headers: Content-Type" \
                 -w "HTTP_CODE:%{http_code}" \
                 http://localhost:8088/api/v1/ai-providers)

CORS_CODE=$(echo "$CORS_TEST" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
if [ "$CORS_CODE" = "200" ] || [ "$CORS_CODE" = "204" ]; then
    echo "✓ CORS preflight successful (HTTP $CORS_CODE)"
else
    echo "⚠ CORS preflight returned HTTP $CORS_CODE (may not be an issue)"
fi

echo ""

# Test 3: Create a quick HTML test that shows if the frontend JS can access the API
echo "3. Creating JavaScript API test page..."
cat > /tmp/api_test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Frontend API Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .success { border-color: green; background: #f0fff0; }
        .error { border-color: red; background: #fff0f0; }
        .loading { border-color: orange; background: #fff8f0; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Frontend API Connection Test</h1>
    <div id="tests"></div>
    
    <script>
        const testsDiv = document.getElementById('tests');
        
        function addTest(name, status, message, data = null) {
            const div = document.createElement('div');
            div.className = `test ${status}`;
            div.innerHTML = `
                <h3>${name}</h3>
                <p>${message}</p>
                ${data ? `<pre>${JSON.stringify(data, null, 2)}</pre>` : ''}
            `;
            testsDiv.appendChild(div);
        }
        
        // Test 1: Basic fetch to API
        addTest('Test 1: Basic API Connection', 'loading', 'Testing...');
        
        fetch('http://localhost:8088/api/v1/ai-providers')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                testsDiv.removeChild(testsDiv.lastChild);
                addTest('Test 1: Basic API Connection', 'success', 
                       `✓ Successfully fetched ${data.length} providers`, data);
                
                // Test 2: Check pricing data
                const providersWithPricing = data.filter(p => p.pricing);
                if (providersWithPricing.length > 0) {
                    addTest('Test 2: Pricing Data', 'success',
                           `✓ Found pricing data for ${providersWithPricing.length} providers`,
                           providersWithPricing.map(p => ({
                               name: p.name,
                               tier: p.pricing.tier,
                               website: p.pricing.websiteUrl
                           })));
                } else {
                    addTest('Test 2: Pricing Data', 'error',
                           '✗ No pricing data found in any provider');
                }
            })
            .catch(error => {
                testsDiv.removeChild(testsDiv.lastChild);
                addTest('Test 1: Basic API Connection', 'error',
                       `✗ API call failed: ${error.message}`);
            });
    </script>
</body>
</html>
EOF

echo "✓ Created API test page at /tmp/api_test.html"
echo ""

echo "4. Next steps:"
echo "   - Open /tmp/api_test.html in your browser to test frontend JS API access"
echo "   - Open browser dev tools and check Console and Network tabs"
echo "   - Look for any CORS errors or network failures"
echo ""
echo "   If the API test shows success but the main app doesn't show pricing:"
echo "   - Clear browser localStorage and cookies"
echo "   - Check if the app is using cached/mock data instead of API data"
echo "   - Verify the AIProviderConfig type matches the API response structure"
