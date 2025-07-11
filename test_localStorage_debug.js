// Test script to debug the exact issue
console.log('=== Testing AI Provider Service Functions ===');

// Import the functions (this would be how they're used in the real app)
const STORAGE_KEY = 'ai-provider-configurations';

// Function to test localStorage operations
function testLocalStorageOperations() {
    console.log('🧪 Testing localStorage operations...');
    
    // Clear everything first
    localStorage.removeItem(STORAGE_KEY);
    console.log('✅ Cleared localStorage');
    
    // Test saving a configuration
    const testConfig = {
        id: 'openai',
        name: 'OpenAI',
        apiKey: 'sk-test123456789',
        isActive: true,
        selectedModel: 'dall-e-3'
    };
    
    // Simulate the updateLocalStorageConfigurations function
    let configurations = [];
    const cached = localStorage.getItem(STORAGE_KEY);
    if (cached) {
        try {
            const parsed = JSON.parse(cached);
            configurations = Array.isArray(parsed) ? parsed : [];
        } catch (parseError) {
            console.error('Parse error:', parseError);
            configurations = [];
        }
    }
    
    // Add the configuration
    const existingIndex = configurations.findIndex(c => c.id === testConfig.id);
    if (existingIndex >= 0) {
        configurations[existingIndex] = { ...configurations[existingIndex], ...testConfig };
    } else {
        configurations.push(testConfig);
    }
    
    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(configurations));
    console.log('💾 Saved configuration:', configurations);
    
    // Test reading back
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        const parsed = JSON.parse(stored);
        console.log('📖 Read back from localStorage:', parsed);
        
        // Test getActiveProviders logic
        const activeProviders = parsed.filter(config => {
            if (!config || typeof config !== 'object') {
                console.warn('Invalid config object:', config);
                return false;
            }
            
            const hasApiKey = config.apiKey && 
                             typeof config.apiKey === 'string' && 
                             config.apiKey.length > 0 && 
                             !config.apiKey.includes('••••');
            const isActive = config.isActive === true;
            
            console.log(`Provider ${config.id}: hasApiKey=${hasApiKey}, isActive=${isActive}`);
            return hasApiKey && isActive;
        });
        
        console.log('🎯 Active providers:', activeProviders);
        
        if (activeProviders.length > 0) {
            console.log('✅ SUCCESS: Configuration persisted and is active');
            return true;
        } else {
            console.log('❌ FAIL: No active providers found');
            return false;
        }
    } else {
        console.log('❌ FAIL: No data found in localStorage');
        return false;
    }
}

// Run the test
const result = testLocalStorageOperations();
console.log('🏁 Test result:', result ? 'PASS' : 'FAIL');
