/**
 * Industry-Specific Templates
 * Phase 1: Quick Wins - Industry-based prompt enhancements
 */

export interface IndustryTemplate {
  id: string;
  name: string;
  visualKeywords: string[];
  styleGuide: string;
  tone: string;
  colorPalette: string[];
  compliance: string[];
  avoidElements: string[];
}

export const INDUSTRY_TEMPLATES: Record<string, IndustryTemplate> = {
  healthcare: {
    id: 'healthcare',
    name: 'Healthcare & Medical',
    visualKeywords: ['clean', 'professional', 'trust', 'care', 'wellness', 'healing'],
    styleGuide: 'Use calming colors (blue, green, white), avoid clinical/scary imagery, emphasize care and compassion',
    tone: 'Empathetic, authoritative, and reassuring',
    colorPalette: ['#0077BE', '#00A86B', '#FFFFFF', '#F0F8FF'],
    compliance: ['HIPAA-compliant imagery', 'diverse representation', 'no identifiable patient info'],
    avoidElements: ['overly clinical tools', 'blood/gore', 'distressed patients']
  },

  technology: {
    id: 'technology',
    name: 'Technology & Software',
    visualKeywords: ['innovative', 'modern', 'sleek', 'digital', 'futuristic', 'efficient'],
    styleGuide: 'Use gradients, geometric shapes, tech aesthetics, modern UI elements, digital backgrounds',
    tone: 'Forward-thinking, accessible, and innovative',
    colorPalette: ['#007AFF', '#5856D6', '#34C759', '#FF9500'],
    compliance: [],
    avoidElements: ['outdated technology', 'cluttered interfaces', 'overly complex diagrams']
  },

  finance: {
    id: 'finance',
    name: 'Finance & Banking',
    visualKeywords: ['secure', 'stable', 'growth', 'professional', 'trustworthy', 'prosperity'],
    styleGuide: 'Use graphs, upward trends, professional settings, secure symbols, wealth indicators',
    tone: 'Confident, reliable, and professional',
    colorPalette: ['#003366', '#006633', '#FFD700', '#FFFFFF'],
    compliance: ['SEC compliance for financial imagery', 'no guaranteed returns imagery'],
    avoidElements: ['risky/gambling imagery', 'get-rich-quick visuals', 'stress/panic imagery']
  },

  retail: {
    id: 'retail',
    name: 'Retail & E-commerce',
    visualKeywords: ['attractive', 'desirable', 'lifestyle', 'shopping', 'trendy', 'value'],
    styleGuide: 'Use product-focused imagery, lifestyle contexts, shopping scenarios, vibrant colors',
    tone: 'Exciting, aspirational, and accessible',
    colorPalette: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF'],
    compliance: [],
    avoidElements: ['empty shelves', 'confused customers', 'price-focus only']
  },

  education: {
    id: 'education',
    name: 'Education & Training',
    visualKeywords: ['learning', 'growth', 'knowledge', 'achievement', 'inspiring', 'accessible'],
    styleGuide: 'Use diverse learners, achievement symbols, collaborative settings, books/learning tools',
    tone: 'Inspiring, supportive, and empowering',
    colorPalette: ['#4A90E2', '#F5A623', '#7ED321', '#FFFFFF'],
    compliance: ['child safety guidelines', 'diverse representation'],
    avoidElements: ['stressed students', 'boring classrooms', 'test anxiety imagery']
  },

  realestate: {
    id: 'realestate',
    name: 'Real Estate & Property',
    visualKeywords: ['home', 'investment', 'lifestyle', 'modern', 'spacious', 'quality'],
    styleGuide: 'Use beautiful properties, welcoming interiors, neighborhood scenes, family-friendly imagery',
    tone: 'Aspirational, trustworthy, and warm',
    colorPalette: ['#8B4513', '#2E8B57', '#F5F5DC', '#4682B4'],
    compliance: ['fair housing compliance', 'no discriminatory imagery'],
    avoidElements: ['distressed properties', 'empty/cold spaces', 'pricing-only focus']
  },

  hospitality: {
    id: 'hospitality',
    name: 'Hospitality & Travel',
    visualKeywords: ['experience', 'luxury', 'comfort', 'adventure', 'relaxation', 'memorable'],
    styleGuide: 'Use destination imagery, happy travelers, luxurious amenities, scenic views',
    tone: 'Welcoming, exciting, and memorable',
    colorPalette: ['#FF6F61', '#6B5B95', '#88B04B', '#F7CAC9'],
    compliance: [],
    avoidElements: ['crowded/chaotic scenes', 'poor service imagery', 'unsafe conditions']
  },

  professional_services: {
    id: 'professional_services',
    name: 'Professional Services',
    visualKeywords: ['expert', 'professional', 'strategic', 'results', 'partnership', 'excellence'],
    styleGuide: 'Use business settings, professional interactions, strategic imagery, success indicators',
    tone: 'Professional, confident, and partnership-focused',
    colorPalette: ['#003366', '#0066CC', '#999999', '#FFFFFF'],
    compliance: [],
    avoidElements: ['overly casual imagery', 'unclear value proposition', 'generic stock photos']
  },

  food_beverage: {
    id: 'food_beverage',
    name: 'Food & Beverage',
    visualKeywords: ['fresh', 'delicious', 'appetizing', 'quality', 'experience', 'artisan'],
    styleGuide: 'Use high-quality food photography, vibrant colors, fresh ingredients, dining experiences',
    tone: 'Appetizing, authentic, and passionate',
    colorPalette: ['#D32F2F', '#F57C00', '#388E3C', '#FBC02D'],
    compliance: ['FDA food imagery guidelines', 'allergen awareness'],
    avoidElements: ['unappetizing presentation', 'processed/artificial look', 'health claims without evidence']
  },

  manufacturing: {
    id: 'manufacturing',
    name: 'Manufacturing & Industrial',
    visualKeywords: ['precision', 'quality', 'innovation', 'efficiency', 'reliable', 'advanced'],
    styleGuide: 'Use modern facilities, precision equipment, quality control, skilled workers, product close-ups',
    tone: 'Reliable, innovative, and quality-focused',
    colorPalette: ['#1565C0', '#424242', '#FF6F00', '#FFFFFF'],
    compliance: ['safety compliance imagery', 'proper PPE representation'],
    avoidElements: ['unsafe conditions', 'outdated equipment', 'poor quality indicators']
  },

  nonprofit: {
    id: 'nonprofit',
    name: 'Nonprofit & Social Impact',
    visualKeywords: ['impact', 'community', 'hope', 'change', 'empowerment', 'solidarity'],
    styleGuide: 'Use real people, authentic stories, positive change, community action, hopeful imagery',
    tone: 'Inspiring, authentic, and action-oriented',
    colorPalette: ['#00897B', '#E91E63', '#FFA726', '#5E35B1'],
    compliance: ['ethical imagery of beneficiaries', 'dignity and respect', 'accurate impact representation'],
    avoidElements: ['poverty porn', 'savior complex imagery', 'exploitation of subjects']
  },

  automotive: {
    id: 'automotive',
    name: 'Automotive',
    visualKeywords: ['performance', 'design', 'innovation', 'freedom', 'adventure', 'luxury'],
    styleGuide: 'Use dynamic angles, motion, sleek designs, lifestyle integration, scenic roads',
    tone: 'Exciting, aspirational, and freedom-focused',
    colorPalette: ['#212121', '#D32F2F', '#1976D2', '#C0C0C0'],
    compliance: ['safety features representation', 'responsible driving imagery'],
    avoidElements: ['reckless driving', 'environmental damage', 'traffic/congestion']
  },

  fitness_wellness: {
    id: 'fitness_wellness',
    name: 'Fitness & Wellness',
    visualKeywords: ['health', 'vitality', 'transformation', 'strength', 'balance', 'energy'],
    styleGuide: 'Use active people, diverse body types, positive energy, natural settings, achievement moments',
    tone: 'Motivating, inclusive, and empowering',
    colorPalette: ['#00C853', '#FF6D00', '#0091EA', '#FFFFFF'],
    compliance: ['body positivity', 'realistic transformation imagery', 'no medical claims'],
    avoidElements: ['body shaming', 'unrealistic transformations', 'dangerous exercises']
  }
};

// Helper function to get industry template
export function getIndustryTemplate(industryId: string): IndustryTemplate | undefined {
  return INDUSTRY_TEMPLATES[industryId];
}

// Helper function to enrich prompt with industry context
export function enrichPromptWithIndustry(
  basePrompt: string, 
  industryId: string,
  translations?: any
): string {
  const template = getIndustryTemplate(industryId);
  
  if (!template) {
    return basePrompt;
  }

  // Use translations if provided, otherwise fallback to English
  const t = translations?.enrichment?.industry || {
    prefix: 'INDUSTRY CONTEXT',
    visual_keywords: 'Visual Keywords',
    style_guide: 'Style Guide',
    tone: 'Tone',
    color_palette: 'Color Palette',
    compliance: 'Compliance',
    avoid: 'Avoid'
  };

  const industryContext = `
${t.prefix} (${template.name}):
- ${t.visual_keywords}: ${template.visualKeywords.join(', ')}
- ${t.style_guide}: ${template.styleGuide}
- ${t.tone}: ${template.tone}
- ${t.color_palette}: ${template.colorPalette.join(', ')}
${template.compliance.length > 0 ? `- ${t.compliance}: ${template.compliance.join(', ')}` : ''}
${template.avoidElements.length > 0 ? `- ${t.avoid}: ${template.avoidElements.join(', ')}` : ''}
`;

  return `${basePrompt}\n\n${industryContext}`;
}
