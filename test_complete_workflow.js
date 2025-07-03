#!/usr/bin/env node

// Comprehensive test of the materials workflow
console.log('=== Testing AI Marketing Agent Workflow ===\n');

// Test 1: Test AI generation endpoint
console.log('1. Testing AI generation endpoint...');
const fetch = require('node-fetch');

async function testAIGeneration() {
  try {
    const response = await fetch('http://localhost:3001/api/v1/ai/generate-image?prompt=test&ai_provider=free-test-provider', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ AI generation endpoint working:', data.success);
      return data;
    } else {
      console.log('❌ AI generation endpoint failed:', response.status);
      return null;
    }
  } catch (error) {
    console.log('❌ AI generation endpoint error:', error.message);
    return null;
  }
}

// Test 2: Check that both servers are running
async function testServers() {
  console.log('\n2. Testing server availability...');
  
  try {
    // Test frontend
    const frontendResponse = await fetch('http://localhost:3001/');
    console.log(`✅ Frontend server: ${frontendResponse.ok ? 'OK' : 'Failed'}`);
    
    // Test API directly
    const apiResponse = await fetch('http://localhost:8089/');
    console.log(`✅ API server: ${apiResponse.status === 404 ? 'OK (404 expected)' : 'Unexpected'}`);
    
    return frontendResponse.ok;
  } catch (error) {
    console.log('❌ Server test failed:', error.message);
    return false;
  }
}

async function runTests() {
  const serversOk = await testServers();
  if (!serversOk) {
    console.log('\n❌ Servers not ready. Please ensure both servers are running.');
    return;
  }
  
  const aiGeneration = await testAIGeneration();
  if (!aiGeneration) {
    console.log('\n❌ AI generation not working.');
    return;
  }
  
  console.log('\n✅ All backend tests passed!');
  console.log('\n🎯 Frontend workflow test:');
  console.log('1. Go to: http://localhost:3001/en/materials/create');
  console.log('2. Fill out the ideation form and submit');
  console.log('3. In refinement phase, select "Free Test Provider"');
  console.log('4. Enter a prompt and click "Generate Image"');
  console.log('5. Verify image generates without errors');
  
  console.log('\n📊 Expected behavior:');
  console.log('- Material created with demo ID (demo-new-[timestamp])');
  console.log('- Free Test Provider should be selectable');
  console.log('- Image generation should complete successfully');
  console.log('- Generated image should appear in the material');
}

runTests().catch(console.error);
