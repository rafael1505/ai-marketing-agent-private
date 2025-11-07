/**
 * Prompt Templates for Material Creation
 * Phase 1: Quick Wins - One-Click Prompt Templates
 */

// Icon components using emojis for consistency
const Rocket = () => <span className="text-2xl">🚀</span>;
const Lightbulb = () => <span className="text-2xl">💡</span>;
const Users = () => <span className="text-2xl">👥</span>;
const TrendingUp = () => <span className="text-2xl">📈</span>;
const Heart = () => <span className="text-2xl">❤️</span>;
const Megaphone = () => <span className="text-2xl">📢</span>;
const Award = () => <span className="text-2xl">🏆</span>;
const Package = () => <span className="text-2xl">📦</span>;

export interface PromptTemplate {
  id: string;
  name: string;
  nameKey: string; // i18n key
  descriptionKey: string; // i18n key
  icon: () => JSX.Element;
  category: 'product' | 'content' | 'engagement' | 'conversion';
  creativeApproach: 'story_led' | 'concept_led' | 'both'; // Storytelling alignment
  structure: {
    focus: string;
    mood: string;
    elements: string[];
    style: string;
    composition: string;
  };
  promptBuilder: (context: PromptContext) => string;
}

export interface PromptContext {
  title: string;
  description?: string;
  targetAudience?: string;
  campaignObjective?: string;
  keywords: string[];
  companyName?: string;
  industry?: string;
}

export const PROMPT_TEMPLATES: PromptTemplate[] = [
  {
    id: "product_launch",
    name: "Product Launch",
    nameKey: "templates.product_launch.name",
    descriptionKey: "templates.product_launch.description",
    icon: Rocket,
    category: "product",
    creativeApproach: "concept_led", // Product-focused, clear visuals
    structure: {
      focus: "product hero shot",
      mood: "exciting, innovative, dynamic",
      elements: ["product in spotlight", "modern background", "premium lighting"],
      style: "commercial photography",
      composition: "centered with depth"
    },
    promptBuilder: (ctx) => `Create a stunning product launch marketing image for "${ctx.title}". 

PRODUCT: ${ctx.description || 'Premium product'}
TARGET: ${ctx.targetAudience || 'Tech-savvy consumers'}
GOAL: ${ctx.campaignObjective || 'Generate excitement and awareness'}

VISUAL REQUIREMENTS:
- Hero shot of the product in spotlight position
- Modern, clean background with subtle gradients
- Professional studio lighting highlighting key features
- Dynamic composition suggesting innovation and quality
- Premium feel with attention to detail
- Colors: Professional, vibrant, eye-catching
- Style: Commercial product photography

Keywords to emphasize: ${ctx.keywords.join(', ')}

The image should evoke excitement, desirability, and make viewers want to learn more about this innovative product.`
  },
  
  {
    id: "thought_leadership",
    name: "Thought Leadership",
    nameKey: "templates.thought_leadership.name",
    descriptionKey: "templates.thought_leadership.description",
    icon: Lightbulb,
    category: "content",
    creativeApproach: "concept_led", // Abstract concepts, visual metaphors
    structure: {
      focus: "abstract concept visualization",
      mood: "professional, authoritative, inspiring",
      elements: ["metaphorical imagery", "clean composition", "strategic elements"],
      style: "abstract conceptual",
      composition: "balanced, sophisticated"
    },
    promptBuilder: (ctx) => `Create a professional thought leadership image for "${ctx.title}".

TOPIC: ${ctx.description || 'Industry insights'}
AUDIENCE: ${ctx.targetAudience || 'Business professionals'}
PURPOSE: ${ctx.campaignObjective || 'Establish authority and credibility'}

VISUAL REQUIREMENTS:
- Abstract, metaphorical representation of concepts
- Professional and sophisticated aesthetic
- Clean, uncluttered composition
- Strategic use of visual metaphors (lightbulbs, pathways, growth symbols)
- Corporate-friendly color palette
- Style: Abstract conceptual art, professional
- No stock photo clichés

Keywords to visualize: ${ctx.keywords.join(', ')}

The image should convey intelligence, insight, and expertise without being overly corporate or boring.`
  },

  {
    id: "social_proof",
    name: "Social Proof",
    nameKey: "templates.social_proof.name",
    descriptionKey: "templates.social_proof.description",
    icon: Users,
    category: "conversion",
    creativeApproach: "story_led", // Real people, authentic stories
    structure: {
      focus: "customer success story",
      mood: "authentic, relatable, trustworthy",
      elements: ["real people", "success indicators", "positive environment"],
      style: "lifestyle photography",
      composition: "natural, candid"
    },
    promptBuilder: (ctx) => `Create an authentic social proof marketing image for "${ctx.title}".

STORY: ${ctx.description || 'Customer success'}
AUDIENCE: ${ctx.targetAudience || 'Potential customers'}
GOAL: ${ctx.campaignObjective || 'Build trust and credibility'}

VISUAL REQUIREMENTS:
- Real, authentic-looking people (diverse, relatable)
- Natural expressions showing satisfaction or success
- Environmental context showing product/service in use
- Positive, uplifting atmosphere
- Success indicators (smiles, achievements, results)
- Style: Lifestyle photography, documentary feel
- Avoid over-staged or fake-looking scenarios

Keywords to emphasize: ${ctx.keywords.join(', ')}

The image should feel genuine and build trust, showing real people benefiting from the product/service.`
  },

  {
    id: "growth_metrics",
    name: "Growth & Results",
    nameKey: "templates.growth_metrics.name",
    descriptionKey: "templates.growth_metrics.description",
    icon: TrendingUp,
    category: "conversion",
    creativeApproach: "concept_led", // Data visualization, clear metrics
    structure: {
      focus: "data visualization and growth",
      mood: "successful, confident, progressive",
      elements: ["upward trends", "charts", "success metrics"],
      style: "infographic style",
      composition: "clear, directional"
    },
    promptBuilder: (ctx) => `Create a compelling growth and results visualization for "${ctx.title}".

ACHIEVEMENT: ${ctx.description || 'Business growth'}
AUDIENCE: ${ctx.targetAudience || 'Decision makers'}
PURPOSE: ${ctx.campaignObjective || 'Demonstrate value and results'}

VISUAL REQUIREMENTS:
- Clean data visualization elements (graphs, charts)
- Clear upward trending indicators
- Professional infographic style
- Success metrics highlighted prominently
- Growth arrows and positive indicators
- Corporate color scheme with accent colors
- Style: Modern infographic, data visualization
- Avoid cluttered or confusing layouts

Keywords to highlight: ${ctx.keywords.join(', ')}

The image should clearly communicate growth, success, and quantifiable results in a visually appealing way.`
  },

  {
    id: "emotional_connection",
    name: "Emotional Connection",
    nameKey: "templates.emotional_connection.name",
    descriptionKey: "templates.emotional_connection.description",
    icon: Heart,
    category: "engagement",
    creativeApproach: "story_led", // Human emotions, genuine moments
    structure: {
      focus: "human emotion and connection",
      mood: "warm, empathetic, heartfelt",
      elements: ["human moments", "connection", "positive emotions"],
      style: "emotional storytelling",
      composition: "intimate, personal"
    },
    promptBuilder: (ctx) => `Create an emotionally engaging marketing image for "${ctx.title}".

MESSAGE: ${ctx.description || 'Emotional connection'}
AUDIENCE: ${ctx.targetAudience || 'Target customers'}
GOAL: ${ctx.campaignObjective || 'Create emotional resonance'}

VISUAL REQUIREMENTS:
- Genuine human moments and emotions
- Warm, inviting color palette
- Intimate, personal composition
- Focus on connection and relationships
- Authentic expressions and interactions
- Style: Emotional storytelling, documentary
- Natural lighting and settings

Keywords to evoke: ${ctx.keywords.join(', ')}

The image should create an emotional connection, making viewers feel something meaningful about the brand or message.`
  },

  {
    id: "announcement",
    name: "Announcement",
    nameKey: "templates.announcement.name",
    descriptionKey: "templates.announcement.description",
    icon: Megaphone,
    category: "engagement",
    creativeApproach: "both", // Works with stories or concepts
    structure: {
      focus: "attention-grabbing announcement",
      mood: "exciting, urgent, important",
      elements: ["bold graphics", "announcement elements", "attention cues"],
      style: "graphic design",
      composition: "bold, impactful"
    },
    promptBuilder: (ctx) => `Create a bold announcement marketing image for "${ctx.title}".

ANNOUNCEMENT: ${ctx.description || 'Important news'}
AUDIENCE: ${ctx.targetAudience || 'Target audience'}
OBJECTIVE: ${ctx.campaignObjective || 'Grab attention and inform'}

VISUAL REQUIREMENTS:
- Bold, attention-grabbing design
- Clear visual hierarchy emphasizing the announcement
- Dynamic composition suggesting importance
- Announcement-style visual elements
- High contrast and visibility
- Style: Graphic design, bold typography-friendly
- Energetic and impactful

Keywords to emphasize: ${ctx.keywords.join(', ')}

The image should immediately grab attention and communicate that something important or exciting is being announced.`
  },

  {
    id: "premium_quality",
    name: "Premium Quality",
    nameKey: "templates.premium_quality.name",
    descriptionKey: "templates.premium_quality.description",
    icon: Award,
    category: "product",
    creativeApproach: "concept_led", // Quality focus, clear imagery
    structure: {
      focus: "luxury and quality",
      mood: "elegant, sophisticated, premium",
      elements: ["luxury details", "quality indicators", "refined aesthetics"],
      style: "high-end photography",
      composition: "refined, sophisticated"
    },
    promptBuilder: (ctx) => `Create a premium quality marketing image for "${ctx.title}".

PRODUCT/SERVICE: ${ctx.description || 'Premium offering'}
AUDIENCE: ${ctx.targetAudience || 'Discerning customers'}
GOAL: ${ctx.campaignObjective || 'Convey luxury and quality'}

VISUAL REQUIREMENTS:
- Elegant, sophisticated aesthetic
- Premium materials and textures visible
- Professional studio-quality lighting
- Refined color palette (blacks, golds, deep colors)
- Attention to craftsmanship and detail
- Style: High-end luxury photography
- Minimal but impactful composition

Keywords to convey: ${ctx.keywords.join(', ')}

The image should exude quality, luxury, and premium value, appealing to customers who appreciate excellence.`
  },

  {
    id: "lifestyle_integration",
    name: "Lifestyle Integration",
    nameKey: "templates.lifestyle_integration.name",
    descriptionKey: "templates.lifestyle_integration.description",
    icon: Package,
    category: "product",
    creativeApproach: "story_led", // Product in lifestyle context with people
    structure: {
      focus: "product in lifestyle context",
      mood: "aspirational, relatable, desirable",
      elements: ["lifestyle setting", "product in use", "aspirational context"],
      style: "lifestyle photography",
      composition: "natural, contextual"
    },
    promptBuilder: (ctx) => `Create a lifestyle integration marketing image for "${ctx.title}".

PRODUCT: ${ctx.description || 'Product or service'}
LIFESTYLE: ${ctx.targetAudience || 'Target lifestyle'}
PURPOSE: ${ctx.campaignObjective || 'Show product enhancing life'}

VISUAL REQUIREMENTS:
- Product naturally integrated into desirable lifestyle
- Aspirational but achievable setting
- Natural, candid composition
- Beautiful, well-designed environment
- Product in contextual use
- Style: Lifestyle photography, editorial
- Warm, inviting atmosphere

Keywords to integrate: ${ctx.keywords.join(', ')}

The image should show how the product fits seamlessly into an aspirational yet relatable lifestyle.`
  },

  {
    id: "brand_identity",
    name: "Brand Identity",
    nameKey: "templates.brand_identity.name",
    descriptionKey: "templates.brand_identity.description",
    icon: Award,
    category: "content",
    creativeApproach: "concept_led", // Brand symbols, visual identity
    structure: {
      focus: "brand essence and values",
      mood: "bold, distinctive, memorable",
      elements: ["brand colors", "symbolic imagery", "strong composition"],
      style: "brand photography",
      composition: "striking, iconic"
    },
    promptBuilder: (ctx) => `Create a bold brand identity image for "${ctx.title}".

BRAND: ${ctx.description || 'Company brand'}
AUDIENCE: ${ctx.targetAudience || 'Brand-conscious consumers'}
GOAL: ${ctx.campaignObjective || 'Strengthen brand recognition'}

VISUAL REQUIREMENTS:
- Strong visual representation of brand identity
- Distinctive and memorable composition
- Strategic use of brand colors and visual language
- Symbolic elements that represent brand values
- Professional, polished aesthetic
- Style: Brand photography, iconic imagery
- No people - focus on brand essence

Keywords to represent: ${ctx.keywords.join(', ')}

The image should instantly communicate what the brand stands for and create lasting visual impact.`
  },

  {
    id: "product_features",
    name: "Product Features",
    nameKey: "templates.product_features.name",
    descriptionKey: "templates.product_features.description",
    icon: Package,
    category: "product",
    creativeApproach: "concept_led", // Feature highlights, technical clarity
    structure: {
      focus: "product features and benefits",
      mood: "informative, clear, professional",
      elements: ["product details", "feature callouts", "clean presentation"],
      style: "technical photography",
      composition: "organized, detailed"
    },
    promptBuilder: (ctx) => `Create a detailed product features image for "${ctx.title}".

PRODUCT: ${ctx.description || 'Product with key features'}
TARGET: ${ctx.targetAudience || 'Feature-focused buyers'}
PURPOSE: ${ctx.campaignObjective || 'Highlight key features and benefits'}

VISUAL REQUIREMENTS:
- Clear, detailed view of product features
- Professional studio lighting to show details
- Clean, organized composition
- Focus on functionality and design
- Technical precision in presentation
- Style: Technical product photography
- No people - product is the hero

Keywords to highlight: ${ctx.keywords.join(', ')}

The image should clearly showcase what makes the product special and why customers should care about its features.`
  },

  {
    id: "abstract_concept",
    name: "Abstract Concept",
    nameKey: "templates.abstract_concept.name",
    descriptionKey: "templates.abstract_concept.description",
    icon: Lightbulb,
    category: "content",
    creativeApproach: "concept_led", // Pure visual metaphors
    structure: {
      focus: "abstract representation",
      mood: "creative, thought-provoking, artistic",
      elements: ["geometric shapes", "symbolic colors", "conceptual forms"],
      style: "abstract art",
      composition: "artistic, interpretive"
    },
    promptBuilder: (ctx) => `Create an abstract conceptual image for "${ctx.title}".

CONCEPT: ${ctx.description || 'Core idea or theme'}
AUDIENCE: ${ctx.targetAudience || 'Creative audience'}
OBJECTIVE: ${ctx.campaignObjective || 'Communicate idea visually'}

VISUAL REQUIREMENTS:
- Abstract, artistic representation of the concept
- Creative use of shapes, colors, and forms
- Thought-provoking visual metaphors
- Modern, contemporary aesthetic
- No literal representations
- Style: Abstract art, conceptual design
- No people - pure concept visualization

Keywords to interpret: ${ctx.keywords.join(', ')}

The image should make viewers think and feel the concept through pure visual language.`
  }
];

// Helper function to get template by ID
export function getTemplateById(id: string): PromptTemplate | undefined {
  return PROMPT_TEMPLATES.find(t => t.id === id);
}

// Helper function to get templates by category
export function getTemplatesByCategory(category: string): PromptTemplate[] {
  return PROMPT_TEMPLATES.filter(t => t.category === category);
}
