console.log('Testing provider loading...');

// Test the constants
import { MARKETING_AI_PROVIDERS } from '../src/constants/marketing-ai-providers';

console.log('Total providers:', MARKETING_AI_PROVIDERS.length);

const freeProviders = MARKETING_AI_PROVIDERS.filter(p => 
  p.pricing?.tier === 'free' || 
  p.configurationStatus === 'configured' ||
  p.isConfigured === true
);

console.log('Available providers:', freeProviders.length);
console.log('Free providers:', freeProviders.map(p => ({ name: p.name, id: p.id, tier: p.pricing?.tier })));

const freeTestProvider = MARKETING_AI_PROVIDERS.find(p => p.id === 'free-test-provider');
console.log('Free Test Provider found:', !!freeTestProvider);
if (freeTestProvider) {
  console.log('Free Test Provider details:', {
    name: freeTestProvider.name,
    isConfigured: freeTestProvider.isConfigured,
    isActive: freeTestProvider.isActive,
    configStatus: freeTestProvider.configurationStatus,
    tier: freeTestProvider.pricing?.tier
  });
}
