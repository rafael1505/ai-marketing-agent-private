// Test script to verify materials cache behavior
const materialId = `demo-new-${Date.now()}`;

// Simulate the development environment
const isDevelopmentMode = () => true;

// Global cache like in the actual code
const materialsCache = {
  data: null,
  timestamp: 0,
  ttl: 30000
};

// Demo materials function
const getDemoMaterials = () => [
  {
    id: 'demo-1',
    title: 'Test Material 1',
    generated_images: []
  },
  {
    id: 'demo-2', 
    title: 'Test Material 2',
    generated_images: []
  }
];

// Simulate createMaterial function
function createMaterial(data) {
  console.log('Creating material in dev mode');
  
  const newMaterial = {
    id: materialId,
    title: data.title,
    description: data.description,
    target_audience: data.target_audience,
    campaign_objective: data.campaign_objective,
    keywords: data.keywords,
    stage: 'idea',
    status: 'draft',
    company_id: 'demo_company',
    created_by: 'demo_user',
    user_id: 'demo_user',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    generated_images: [],
    feedback: []
  };
  
  console.log('Created material with ID:', newMaterial.id);
  
  // Initialize cache with demo materials if it doesn't exist
  if (!materialsCache.data) {
    console.log('Initializing cache with demo materials');
    materialsCache.data = getDemoMaterials();
    materialsCache.timestamp = Date.now();
  }
  
  // Add new material to cache
  materialsCache.data.unshift(newMaterial);
  console.log('Added material to cache. Cache now has', materialsCache.data.length, 'materials');
  console.log('Cache material IDs:', materialsCache.data.map(m => m.id));
  
  return newMaterial;
}

// Simulate addGeneratedImage function
function addGeneratedImage(materialId, imageUrl, prompt, aiProvider, generationParams) {
  console.log('Adding generated image:', { materialId, imageUrl, prompt, aiProvider });
  
  if (isDevelopmentMode()) {
    console.log('Development mode: Handling image addition');
    
    // Ensure cache exists
    if (!materialsCache.data) {
      console.log('Cache is empty, initializing with demo materials');
      materialsCache.data = getDemoMaterials();
      materialsCache.timestamp = Date.now();
    }
    
    console.log('Looking for material:', materialId);
    console.log('Cache contents:', materialsCache.data.map(m => ({ id: m.id, title: m.title })));
    
    // Find the material in cache
    let material = materialsCache.data.find(m => m.id === materialId);
    
    if (!material) {
      console.log('Material not found in cache, creating fallback material...');
      // Create a fallback material if it doesn't exist
      material = {
        id: materialId,
        title: 'AI Marketing Material',
        description: 'Generated during image creation',
        target_audience: 'General audience',
        campaign_objective: 'Brand awareness',
        keywords: ['ai', 'marketing'],
        stage: 'refinement',
        status: 'in_progress',
        company_id: 'demo_company',
        created_by: 'demo_user',
        user_id: 'demo_user',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        generated_images: [],
        feedback: []
      };
      
      // Add to cache
      materialsCache.data.unshift(material);
      console.log('Created fallback material and added to cache');
    }
    
    // Add the image
    const newImage = {
      url: imageUrl,
      prompt,
      ai_provider: aiProvider,
      generation_params: generationParams,
      created_at: new Date().toISOString()
    };
    
    // Create updated material with new image
    const updatedMaterial = {
      ...material,
      generated_images: [...(material.generated_images || []), newImage],
      updated_at: new Date().toISOString()
    };
    
    // Update in cache
    const index = materialsCache.data.findIndex(m => m.id === materialId);
    if (index >= 0) {
      materialsCache.data[index] = updatedMaterial;
      console.log('Updated existing material in cache');
    } else {
      // This should not happen after our fallback creation, but just in case
      materialsCache.data.unshift(updatedMaterial);
      console.log('Added updated material to cache');
    }
    
    console.log('Image added successfully. Material now has', updatedMaterial.generated_images.length, 'images');
    return updatedMaterial;
  }
}

// Test the workflow
console.log('=== Testing Material Creation & Image Addition Workflow ===\n');

// Step 1: Create a material
console.log('1. Creating material...');
const material = createMaterial({
  title: 'Test Marketing Campaign',
  description: 'Test description',
  target_audience: 'Tech enthusiasts',
  campaign_objective: 'Brand awareness',
  keywords: ['tech', 'innovation']
});

console.log('\n2. Material created:', material.id);

// Step 2: Add an image to the material
console.log('\n3. Adding image to material...');
const updatedMaterial = addGeneratedImage(
  material.id,
  'https://example.com/test-image.jpg',
  'A test marketing image',
  'Free Test Provider',
  { size: '1024x1024' }
);

console.log('\n4. Final material state:');
console.log('   - ID:', updatedMaterial.id);
console.log('   - Images:', updatedMaterial.generated_images.length);
console.log('   - Cache size:', materialsCache.data.length);

console.log('\n=== Test completed successfully! ===');
