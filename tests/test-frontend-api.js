#!/usr/bin/env node

// Simple test to simulate what the frontend is doing
const axios = require('axios');

async function testFrontendAPI() {
    console.log('Testing frontend API calls...');
    
    // Test the API URL that the frontend uses
    const API_URL = 'http://127.0.0.1:3001/api/v1';
    
    try {
        console.log('1. Testing getAvailableProviders...');
        const providersResponse = await axios.get(`${API_URL}/ai/providers`);
        console.log('Providers response:', providersResponse.data);
        
        console.log('2. Testing getProviderConfigurations...');
        const configsResponse = await axios.get(`${API_URL}/ai-providers/configurations`);
        console.log('Configs response:', configsResponse.data);
        
        console.log('3. All API calls successful!');
    } catch (error) {
        console.error('API test failed:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', error.response.data);
        }
    }
}

testFrontendAPI();
