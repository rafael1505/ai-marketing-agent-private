// Test script to check if frontend can fetch API data
console.log("Testing frontend API connection...");

fetch("http://localhost:8088/api/v1/ai-providers")
  .then(response => {
    console.log("Response status:", response.status);
    console.log("Response headers:", response.headers);
    return response.json();
  })
  .then(data => {
    console.log("API Response:", data);
    console.log("Number of providers:", data.length);
    
    data.forEach(provider => {
      console.log(`\nProvider: ${provider.name}`);
      console.log(`  ID: ${provider.id}`);
      console.log(`  Pricing Tier: ${provider.pricing.tier}`);
      console.log(`  Website: ${provider.pricing.websiteUrl}`);
      
      if (provider.pricing.freeQuota) {
        console.log(`  Free Quota: ${provider.pricing.freeQuota.description}`);
      }
      
      if (provider.pricing.paidPlans) {
        console.log(`  Paid Plans: ${provider.pricing.paidPlans.length} plan(s)`);
        provider.pricing.paidPlans.forEach(plan => {
          console.log(`    - ${plan.name}: ${plan.description}`);
        });
      }
    });
  })
  .catch(error => {
    console.error("Error fetching data:", error);
  });
