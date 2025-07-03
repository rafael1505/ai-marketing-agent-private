// Test the exact image generation flow that's causing the error
const testMaterialId = 'demo-new-1751570105054';
const imageUrl = 'https://example.com/test-image.jpg';
const prompt = 'Test marketing image';
const aiProvider = 'free-test-provider';
const generationParams = { size: '1024x1024', style: 'photorealistic' };

console.log('=== Testing Image Generation Flow ===');
console.log('Material ID:', testMaterialId);
console.log('Frontend URL: http://localhost:3001');

// Create URL with query parameters as the frontend would
const baseUrl = 'http://localhost:3001/api/materials';
const addImageUrl = `${baseUrl}/${testMaterialId}/images?url=${encodeURIComponent(imageUrl)}&prompt=${encodeURIComponent(prompt)}&ai_provider=${encodeURIComponent(aiProvider)}&generation_params=${encodeURIComponent(JSON.stringify(generationParams))}`;

console.log('Full URL:', addImageUrl);

// Test the API call
const { exec } = require('child_process');

exec(`curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzUzMjI5OGY4YzU1M2I0NGZhOGYzZGIiLCJjb21wYW55X2lkIjoidGVzdF9jb21wYW55IiwiZXhwIjoxNzQzNTU2MzMwfQ.3L55qOOTKbpllPGM7kxFnHd1v3xWMaXNpfSHJjSHB5Y" "${addImageUrl}"`, (error, stdout, stderr) => {
  if (error) {
    console.error('❌ Error:', error.message);
    return;
  }
  
  if (stderr) {
    console.error('❌ Stderr:', stderr);
    return;
  }
  
  console.log('✅ Response:', stdout);
  
  // Check if the response contains the expected error
  if (stdout.includes('not found in demo mode')) {
    console.log('🔥 CONFIRMED: The "not found in demo mode" error is coming from the API response');
    console.log('🔥 This means the frontend IS making an API call when it should be using local cache');
  } else {
    console.log('✅ No "not found in demo mode" error detected');
  }
});
