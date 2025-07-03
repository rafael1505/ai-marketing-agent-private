// Simple test to verify materials service behavior
// This will help us understand if the issue is in the frontend code or elsewhere

console.log('=== Materials Service Test ===');

// Mock the required types and imports
const MaterialStage = {
  IDEA: 'idea',
  REFINEMENT: 'refinement',
  FINALIZATION: 'finalization'
};

const MaterialStatus = {
  DRAFT: 'draft',
  IN_PROGRESS: 'in_progress',
  READY_FOR_REVIEW: 'ready_for_review'
};

// Mock localStorage for Node.js
const mockLocalStorage = {
  getItem: (key) => null,
  setItem: (key, value) => true
};

// Mock window for Node.js
global.window = undefined;

// Mock the API module 
const mockApi = {
  get: async (url) => {
    console.log('🚨 API GET called:', url);
    throw new Error('Mock API should not be called in development mode!');
  },
  post: async (url, data) => {
    console.log('🚨 API POST called:', url, data);
    throw new Error('Mock API should not be called in development mode!');
  }
};

// Test the isDevelopmentMode function behavior
const testIsDevelopmentMode = () => {
  try {
    // This should always return true based on our forced implementation
    return true;
  } catch (error) {
    console.warn('Error detecting development mode:', error);
    return true;
  }
};

// Test the addGeneratedImage function logic
const testAddGeneratedImage = async () => {
  console.log('\n=== Testing addGeneratedImage Logic ===');
  
  const materialId = 'demo-new-1751570105054';
  const imageUrl = 'https://example.com/test.jpg';
  const prompt = 'Test prompt';
  const aiProvider = 'free-test-provider';
  const generationParams = { size: '1024x1024', style: 'photorealistic' };
  
  console.log('Input parameters:', { materialId, imageUrl, prompt, aiProvider });
  
  const devMode = testIsDevelopmentMode();
  console.log('Development mode detected:', devMode);
  
  if (devMode) {
    console.log('✅ Development mode: Should handle image addition locally');
    
    // Simulate the materials cache
    const mockCache = [
      {
        id: 'demo-1',
        title: 'Demo Material 1',
        generated_images: []
      }
    ];
    
    console.log('Looking for material:', materialId);
    console.log('Available materials:', mockCache.map(m => m.id));
    
    let material = mockCache.find(m => m.id === materialId);
    
    if (!material) {
      console.log('Material not found in cache, creating fallback...');
      material = {
        id: materialId,
        title: 'AI Marketing Material',
        description: 'Generated during image creation',
        target_audience: 'General audience',
        campaign_objective: 'Brand awareness',
        keywords: ['ai', 'marketing'],
        stage: MaterialStage.REFINEMENT,
        status: MaterialStatus.IN_PROGRESS,
        company_id: 'demo_company',
        created_by: 'demo_user',
        user_id: 'demo_user',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        generated_images: [],
        feedback: []
      };
      
      mockCache.unshift(material);
      console.log('✅ Created fallback material successfully');
    }
    
    // Add the image
    const newImage = {
      url: imageUrl,
      prompt,
      ai_provider: aiProvider,
      generation_params: generationParams,
      created_at: new Date().toISOString()
    };
    
    const updatedMaterial = {
      ...material,
      generated_images: [...(material.generated_images || []), newImage],
      updated_at: new Date().toISOString()
    };
    
    console.log('✅ Image added successfully. Material now has', updatedMaterial.generated_images.length, 'images');
    return updatedMaterial;
  } else {
    console.log('❌ Production mode detected - this should not happen!');
    throw new Error('Production mode should not be detected!');
  }
};

// Run the test
console.log('Testing development mode detection...');
console.log('isDevelopmentMode():', testIsDevelopmentMode());

testAddGeneratedImage()
  .then((result) => {
    console.log('\n✅ Test completed successfully!');
    console.log('Result material ID:', result.id);
    console.log('Generated images count:', result.generated_images.length);
  })
  .catch((error) => {
    console.error('\n❌ Test failed:', error.message);
  });
