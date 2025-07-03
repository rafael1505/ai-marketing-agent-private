// Debug script to test the exact frontend flow
const { exec } = require('child_process');

// Test the frontend flow by making a request to the Next.js server
// which should trigger the frontend code path

console.log('Testing frontend flow...');

// First, test if we can reach the Next.js server
exec('curl -s http://localhost:3000/en/materials/create', (error, stdout, stderr) => {
  if (error) {
    console.error('Error reaching frontend:', error.message);
    return;
  }
  
  if (stderr) {
    console.error('Frontend stderr:', stderr);
    return;
  }
  
  console.log('Frontend is accessible');
  
  // Test the materials API endpoint through the Next.js proxy
  exec('curl -s -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzUzMjI5OGY4YzU1M2I0NGZhOGYzZGIiLCJjb21wYW55X2lkIjoidGVzdF9jb21wYW55IiwiZXhwIjoxNzQzNTU2MzMwfQ.3L55qOOTKbpllPGM7kxFnHd1v3xWMaXNpfSHJjSHB5Y" http://localhost:3000/api/materials', (error, stdout, stderr) => {
    if (error) {
      console.error('Error reaching materials API:', error.message);
      return;
    }
    
    if (stderr) {
      console.error('Materials API stderr:', stderr);
      return;
    }
    
    console.log('Materials API response:', stdout);
    
    // Now test the image generation endpoint
    const testMaterialId = 'demo-new-' + Date.now();
    const imageUrl = 'https://example.com/test.jpg';
    const prompt = 'Test prompt';
    const aiProvider = 'free-test-provider';
    const generationParams = JSON.stringify({ size: '1024x1024', style: 'photorealistic' });
    
    const addImageUrl = `http://localhost:3000/api/materials/${testMaterialId}/images?url=${encodeURIComponent(imageUrl)}&prompt=${encodeURIComponent(prompt)}&ai_provider=${encodeURIComponent(aiProvider)}&generation_params=${encodeURIComponent(generationParams)}`;
    
    console.log('Testing image addition with URL:', addImageUrl);
    
    exec(`curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzUzMjI5OGY4YzU1M2I0NGZhOGYzZGIiLCJjb21wYW55X2lkIjoidGVzdF9jb21wYW55IiwiZXhwIjoxNzQzNTU2MzMwfQ.3L55qOOTKbpllPGM7kxFnHd1v3xWMaXNpfSHJjSHB5Y" "${addImageUrl}"`, (error, stdout, stderr) => {
      if (error) {
        console.error('Error adding image:', error.message);
        return;
      }
      
      if (stderr) {
        console.error('Add image stderr:', stderr);
        return;
      }
      
      console.log('Add image response:', stdout);
    });
  });
});
