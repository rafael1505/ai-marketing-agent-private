const axios = require('axios');

// Mimic the frontend API configuration
const API_URL = '/api/v1';
const BASE_URL = 'http://127.0.0.1:3001';

const api = axios.create({
  baseURL: BASE_URL + API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlzX2FkbWluIjp0cnVlLCJpYXQiOjE3NTE0OTY4NjUsImV4cCI6MTc1NDA4ODg2NX0.1QglhuJU3ipmB1qt74lIRvhU-xk3-UkiwFBuzVvcYWc'
  },
  timeout: 15000,
});

async function testAPI() {
  console.log('Testing API configuration...');
  console.log('Full base URL:', BASE_URL + API_URL);
  
  try {
    // Test ping first
    console.log('\n1. Testing ping endpoint...');
    const pingResponse = await api.get('/diagnostic/ping');
    console.log('Ping successful:', pingResponse.data);
    
    // Test auth verification
    console.log('\n2. Testing auth verification...');
    const authResponse = await api.post('/auth/verify-token');
    console.log('Auth verification successful:', authResponse.data);
    
    // Test materials endpoint
    console.log('\n3. Testing materials list...');
    const materialsResponse = await api.get('/materials');
    console.log('Materials list successful:', materialsResponse.data);
    
    // Test adding image to a material (simulated)
    console.log('\n4. Testing add image endpoint...');
    const materialId = 'test123';
    const fullUrl = `/materials/${materialId}/images?url=${encodeURIComponent('http://example.com/image.jpg')}&prompt=${encodeURIComponent('test prompt')}&ai_provider=${encodeURIComponent('openai')}&generation_params=${encodeURIComponent(JSON.stringify({}))}`;
    console.log('Full URL for image addition:', fullUrl);
    console.log('Complete URL:', BASE_URL + API_URL + fullUrl);
    
    const imageResponse = await api.post(fullUrl);
    console.log('Add image successful:', imageResponse.data);
    
  } catch (error) {
    console.error('API test failed:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    });
  }
}

testAPI();
