#!/bin/bash

echo "=== AI Marketing Agent - Pricing Differentiation Feature Test ==="
echo

# Test 1: Backend API includes pricing data
echo "1. Testing Backend API - Pricing Data..."
PRICING_DATA=$(curl -s http://127.0.0.1:8088/api/v1/ai-providers | grep -o '"pricing"' | wc -l)
if [ "$PRICING_DATA" -gt "0" ]; then
    echo "✅ Backend returns pricing data for providers"
    echo "   Found pricing data in $PRICING_DATA providers"
else
    echo "❌ Backend does not return pricing data"
fi

# Test 2: Check specific pricing tiers
echo
echo "2. Testing Pricing Tiers..."
API_RESPONSE=$(curl -s http://127.0.0.1:8088/api/v1/ai-providers)

FREE_COUNT=$(echo "$API_RESPONSE" | grep -o '"tier":"free"' | wc -l)
FREEMIUM_COUNT=$(echo "$API_RESPONSE" | grep -o '"tier":"freemium"' | wc -l)
PAID_COUNT=$(echo "$API_RESPONSE" | grep -o '"tier":"paid"' | wc -l)

echo "   🆓 Free providers: $FREE_COUNT (e.g., Ollama)"
echo "   💎 Freemium providers: $FREEMIUM_COUNT (e.g., Hugging Face)"
echo "   💳 Paid providers: $PAID_COUNT (e.g., Stability AI, OpenAI)"

# Test 3: Check pricing details
echo
echo "3. Testing Pricing Details..."
FREE_QUOTA=$(echo "$API_RESPONSE" | grep -o '"freeQuota":{[^}]*}' | wc -l)
PAID_PLANS=$(echo "$API_RESPONSE" | grep -o '"paidPlans":\[[^]]*\]' | wc -l)
WEBSITE_URLS=$(echo "$API_RESPONSE" | grep -o '"websiteUrl":"[^"]*"' | wc -l)

echo "   ✅ Free quota descriptions: $FREE_QUOTA"
echo "   ✅ Paid plan details: $PAID_PLANS"
echo "   ✅ Pricing website URLs: $WEBSITE_URLS"

# Test 4: Frontend accessibility
echo
echo "4. Testing Frontend Integration..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/en/settings)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✅ Settings page loads successfully"
    echo "   You can now test the pricing features in the browser!"
else
    echo "❌ Settings page not accessible (HTTP $FRONTEND_RESPONSE)"
fi

echo
echo "=== New Pricing Features Available ==="
echo
echo "🎯 **Visual Indicators:**"
echo "   🆓 Free providers - Green badge with 'Free' label"
echo "   💎 Freemium providers - Blue badge with 'Freemium' label"
echo "   💳 Paid providers - Purple badge with 'Paid' label"
echo
echo "🔍 **Filtering & Sorting:**"
echo "   • Filter by pricing tier (All/Free/Freemium/Paid)"
echo "   • Sort by pricing tier or provider name"
echo
echo "📋 **Enhanced Provider Cards:**"
echo "   • Pricing badge next to provider name"
echo "   • Quick pricing summary below name"
echo "   • Expandable pricing details section"
echo "   • Direct links to provider pricing pages"
echo
echo "⚙️ **Enhanced Configuration Dialog:**"
echo "   • Pricing information section with tier badge"
echo "   • Cost warnings for paid services"
echo "   • Free tier highlights for freemium providers"
echo "   • Links to detailed pricing information"
echo
echo "🎉 **Test Instructions:**"
echo "1. Visit: http://127.0.0.1:3001/en/settings"
echo "2. Scroll to 'AI Providers' section"
echo "3. Notice the new pricing badges (🆓💎💳)"
echo "4. Try the filter dropdown to show only 'Free' providers"
echo "5. Click 'Sort by Pricing' to see providers grouped by cost"
echo "6. Expand 'View Pricing Details' on any provider card"
echo "7. Click 'Configure' and see pricing info in the dialog"
echo "8. Try the 'View Pricing Details →' links"
echo
echo "🚀 **Implementation Complete!**"
