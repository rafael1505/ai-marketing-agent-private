// Browser console test for getUserAIProviders function
// Copy and paste this into your browser's developer console

console.log("🧪 Testing getUserAIProviders function directly in browser...");

// Clear any existing cache
localStorage.removeItem('ai_provider_configs');
console.log("🗑️ Cleared localStorage cache");

// Test direct fetch to the API
fetch('/api/v1/ai-providers')
  .then(response => {
    console.log("📡 API Response status:", response.status);
    return response.json();
  })
  .then(data => {
    console.log("📥 API returned", data.length, "providers");
    console.log("📥 Provider list:", data.map(p => `${p.name} (configured: ${p.isConfigured})`));
    
    const openai = data.find(p => p.id === 'openai');
    if (openai) {
      console.log("✅ OpenAI found in API data:", openai);
    } else {
      console.log("❌ OpenAI NOT found in API data");
    }
    
    // Now test the getUserAIProviders function behavior
    console.log("\n🔄 Simulating getUserAIProviders logic...");
    
    // Simulate the fixed logic (should include all providers)
    console.log("💾 Storing all providers in localStorage...");
    localStorage.setItem('ai_provider_configs', JSON.stringify(data));
    
    // Test retrieval
    const cached = localStorage.getItem('ai_provider_configs');
    if (cached) {
      const parsed = JSON.parse(cached);
      console.log("📦 Retrieved from localStorage:", parsed.length, "providers");
      
      const cachedOpenai = parsed.find(p => p.id === 'openai');
      if (cachedOpenai) {
        console.log("✅ OpenAI found in cached data:", cachedOpenai);
      } else {
        console.log("❌ OpenAI NOT found in cached data");
      }
    }
  })
  .catch(error => {
    console.error("❌ Error testing API:", error);
  });

// Also test what the actual getUserAIProviders function returns
setTimeout(() => {
  console.log("\n🎯 If getUserAIProviders function is available, testing it...");
  if (typeof getUserAIProviders !== 'undefined') {
    getUserAIProviders().then(result => {
      console.log("📋 getUserAIProviders returned:", result.length, "providers");
      const openai = result.find(p => p.id === 'openai');
      if (openai) {
        console.log("✅ getUserAIProviders includes OpenAI:", openai);
      } else {
        console.log("❌ getUserAIProviders does NOT include OpenAI");
        console.log("📋 Providers returned:", result.map(p => p.name));
      }
    }).catch(e => {
      console.error("❌ getUserAIProviders error:", e);
    });
  } else {
    console.log("ℹ️ getUserAIProviders function not available in global scope");
  }
}, 1000);