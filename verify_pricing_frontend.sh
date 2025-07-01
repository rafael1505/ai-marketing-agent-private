#!/bin/bash

# Script to verify frontend is showing latest pricing data

echo "=== Frontend Pricing Verification Script ==="
echo ""

# Test 1: Check backend API is serving pricing data
echo "1. Testing backend API..."
API_RESPONSE=$(curl -s http://localhost:8088/api/v1/ai-providers)
if [ $? -eq 0 ]; then
    echo "✓ Backend API is responding"
    echo "   Number of providers: $(echo "$API_RESPONSE" | grep -o '"name"' | wc -l)"
    
    # Check if pricing data is present
    if echo "$API_RESPONSE" | grep -q '"pricing"'; then
        echo "✓ Pricing data is present in API response"
        
        # Extract pricing tiers
        echo "   Pricing tiers found:"
        echo "$API_RESPONSE" | grep -o '"tier":"[^"]*"' | sort | uniq | sed 's/"tier":"/ - /' | sed 's/"$//'
    else
        echo "✗ No pricing data found in API response"
        exit 1
    fi
else
    echo "✗ Backend API is not responding"
    exit 1
fi

echo ""

# Test 2: Check frontend is accessible
echo "2. Testing frontend accessibility..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/en/settings)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✓ Frontend is accessible"
else
    echo "✗ Frontend returned status code: $FRONTEND_RESPONSE"
fi

echo ""

# Test 3: Create a test HTML page to verify frontend-backend connection
echo "3. Creating frontend test page..."
cat > /tmp/pricing_test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Pricing Data Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .provider { border: 1px solid #ccc; margin: 10px; padding: 15px; }
        .tier { font-weight: bold; color: #007acc; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1>AI Providers Pricing Test</h1>
    <div id="status">Loading...</div>
    <div id="providers"></div>
    
    <script>
        async function testPricingData() {
            const statusDiv = document.getElementById('status');
            const providersDiv = document.getElementById('providers');
            
            try {
                console.log('Fetching data from API...');
                const response = await fetch('http://localhost:8088/api/v1/ai-providers');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const providers = await response.json();
                console.log('Received providers:', providers);
                
                statusDiv.innerHTML = `<span class="success">✓ Successfully fetched ${providers.length} providers</span>`;
                
                providers.forEach(provider => {
                    const div = document.createElement('div');
                    div.className = 'provider';
                    
                    let html = `
                        <h3>${provider.name} (${provider.id})</h3>
                        <p><strong>Pricing Tier:</strong> <span class="tier">${provider.pricing.tier}</span></p>
                    `;
                    
                    if (provider.pricing.websiteUrl) {
                        html += `<p><strong>Website:</strong> <a href="${provider.pricing.websiteUrl}" target="_blank">${provider.pricing.websiteUrl}</a></p>`;
                    }
                    
                    if (provider.pricing.freeQuota) {
                        html += `<p><strong>Free Quota:</strong> ${provider.pricing.freeQuota.description}</p>`;
                    }
                    
                    if (provider.pricing.paidPlans && provider.pricing.paidPlans.length > 0) {
                        html += '<p><strong>Paid Plans:</strong></p><ul>';
                        provider.pricing.paidPlans.forEach(plan => {
                            html += `<li>${plan.name}: ${plan.description}</li>`;
                        });
                        html += '</ul>';
                    }
                    
                    div.innerHTML = html;
                    providersDiv.appendChild(div);
                });
                
            } catch (error) {
                console.error('Error:', error);
                statusDiv.innerHTML = `<span class="error">✗ Error: ${error.message}</span>`;
            }
        }
        
        // Run test when page loads
        testPricingData();
    </script>
</body>
</html>
EOF

echo "✓ Test page created at /tmp/pricing_test.html"
echo ""

# Test 4: Instructions for manual verification
echo "4. Manual verification steps:"
echo "   a) Open http://localhost:3001/en/settings in your browser"
echo "   b) Look for pricing badges (Free, Freemium, Paid) on provider cards"
echo "   c) Check if pricing filter dropdown is available"
echo "   d) Click on a provider to see pricing details in the dialog"
echo ""
echo "   Alternative: Open /tmp/pricing_test.html in your browser"
echo "   to see raw API data visualization"
echo ""

echo "=== Verification Complete ==="
echo ""
echo "If pricing badges are not visible in the frontend:"
echo "1. Clear browser cache and localStorage"
echo "2. Hard refresh the page (Ctrl+F5)"
echo "3. Check browser console for JavaScript errors"
echo "4. Verify the frontend is making API calls to localhost:8088"
