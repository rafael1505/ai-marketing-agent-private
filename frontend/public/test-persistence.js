// Company Persistence Test Script
// Paste this into the browser console at http://127.0.0.1:3001/en/settings

console.log("🧪 Starting Company Persistence Test");

// Set authentication token if not already set
const testToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc0ODYxMzg4OCwiZXhwIjoxNzUxMjA1ODg4fQ._mI_ZPS8TvP2CUGkWvERtqKZzjiiisGiFcVeRWQOick";

if (!localStorage.getItem('token')) {
    console.log("Setting authentication token...");
    localStorage.setItem('token', testToken);
    console.log("✅ Token set!");
} else {
    console.log("✅ Token already exists");
}

// Test function
async function testCompanyPersistence() {
    console.log("\n1. Getting current company...");
    
    try {
        // Get current company data
        const currentResponse = await fetch('/api/v1/companies/active');
        const currentCompany = await currentResponse.json();
        console.log("Current company:", currentCompany.name);
        console.log("Current colors:", currentCompany.brand_colors);
        
        // Prepare update data
        const timestamp = Date.now();
        const formData = new FormData();
        formData.append('name', `Updated Company ${timestamp}`);
        formData.append('description', `Updated at ${new Date().toISOString()}`);
        formData.append('email', 'test@updated.com');
        formData.append('phone', '+1-555-UPDATED');
        formData.append('address', '123 Updated Street');
        formData.append('brand_colors[0]', '#FF0000'); // Red
        formData.append('brand_colors[1]', '#00FF00'); // Green
        formData.append('brand_colors[2]', '#0000FF'); // Blue
        
        console.log("\n2. Updating company with authentication...");
        
        // Update company
        const updateResponse = await fetch('/api/v1/companies/test_company', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        console.log("Update status:", updateResponse.status);
        
        if (updateResponse.ok) {
            const updatedCompany = await updateResponse.json();
            console.log("✅ Update successful!");
            console.log("Updated name:", updatedCompany.name);
            console.log("Updated colors:", updatedCompany.brand_colors);
            
            // Wait a moment and check persistence
            console.log("\n3. Checking persistence in 3 seconds...");
            setTimeout(async () => {
                const finalResponse = await fetch('/api/v1/companies/active');
                const finalCompany = await finalResponse.json();
                
                console.log("Final name:", finalCompany.name);
                console.log("Final colors:", finalCompany.brand_colors);
                
                const nameChanged = finalCompany.name !== currentCompany.name;
                const colorsChanged = JSON.stringify(finalCompany.brand_colors) !== JSON.stringify(currentCompany.brand_colors);
                
                console.log("\n📊 RESULTS:");
                console.log("Name changed:", nameChanged);
                console.log("Colors changed:", colorsChanged);
                
                if (nameChanged && colorsChanged) {
                    console.log("🎉 SUCCESS: Changes persisted!");
                } else {
                    console.log("❌ FAILURE: Changes did not persist");
                }
                
                // Refresh the page to see changes in UI
                console.log("\n🔄 Refreshing page to see changes...");
                setTimeout(() => window.location.reload(), 2000);
            }, 3000);
            
        } else {
            const errorText = await updateResponse.text();
            console.log("❌ Update failed:", errorText);
        }
        
    } catch (error) {
        console.error("❌ Test failed:", error);
    }
}

// Run the test
console.log("Starting test in 2 seconds...");
setTimeout(testCompanyPersistence, 2000);
