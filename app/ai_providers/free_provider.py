"""
Free AI Provider Implementation
Generates placeholder images for testing without requiring API keys
"""
import random
from typing import Dict, Any

class FreeTestProvider:
    """Free test provider that generates placeholder images"""
    
    def __init__(self):
        self.name = "Free Test Provider"
        self.id = "free-test-provider"
        self.is_configured = True
        
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a placeholder image URL based on the prompt"""
        
        # Generate different placeholder images based on prompt keywords
        size = kwargs.get('size', '1024x1024')
        width, height = size.split('x') if 'x' in size else ('1024', '1024')
        
        # Normalize prompt for analysis (handle both English and Portuguese)
        prompt_lower = prompt.lower()
        
        # Enhanced keyword detection with comprehensive Portuguese support
        business_keywords = ['business', 'meeting', 'office', 'corporate', 'company', 'professional',
                           'trabalho', 'escritório', 'reunião', 'empresa', 'corporativo', 'profissional',
                           'negócios', 'corporação', 'comercial']
        
        celebration_keywords = ['celebration', 'party', 'festive', 'happy', 'joy', 'success', 'achievement',
                              'celebração', 'festa', 'comemoração', 'alegria', 'felicidade', 'sucesso',
                              'conquista', 'vitória', 'festejo', 'celebrar']
        
        work_keywords = ['work', 'workers', 'employees', 'team', 'staff', 'workplace', 'labor',
                        'trabalho', 'funcionários', 'equipe', 'trabalhadores', 'colaboradores',
                        'empregados', 'pessoal', 'mão de obra', 'local de trabalho']
        
        email_keywords = ['email', 'newsletter', 'communication', 'marketing', 'campaign', 'digital',
                         'comunicação', 'comunicado', 'campanha', 'divulgação', 'propaganda', 'publicidade']
        
        people_keywords = ['people', 'person', 'human', 'group', 'crowd', 'individual',
                          'pessoas', 'pessoa', 'humano', 'gente', 'grupo', 'multidão', 'indivíduo']
        
        # Special Labor Day detection (more comprehensive)
        labor_day_keywords = ['dia do trabalho', 'labor day', 'workers day', 'may day', 
                             'primeiro de maio', '1º de maio', 'feriado do trabalho']
        
        # Determine the most appropriate theme with better logic
        detected_language = 'pt' if any(word in prompt_lower for word in 
                                       ['trabalho', 'funcionários', 'celebração', 'festa', 'empresa', 
                                        'profissional', 'comunicação', 'pessoas', 'alegria']) else 'en'
        
        if any(keyword in prompt_lower for keyword in labor_day_keywords):
            seed = 'labor-day-celebration'
            theme = 'work+celebration'
        elif any(word in prompt_lower for word in celebration_keywords):
            if any(word in prompt_lower for word in work_keywords + business_keywords):
                seed = 'work-celebration'
                theme = 'work+celebration'
            else:
                seed = 'celebration'
                theme = 'celebration'
        elif any(word in prompt_lower for word in work_keywords):
            seed = 'workplace'
            theme = 'work'
        elif any(word in prompt_lower for word in business_keywords):
            seed = 'business'
            theme = 'business'
        elif any(word in prompt_lower for word in email_keywords):
            seed = 'marketing'
            theme = 'marketing'
        elif any(word in prompt_lower for word in people_keywords):
            seed = 'people'
            theme = 'people'
        else:
            seed = 'business'  # Default to business for professional content
            theme = 'business'
        
        # Generate a unique ID for this image
        image_id = random.randint(100, 999)
        
        # Use more contextual placeholder services with better variety
        if theme == 'work+celebration':
            # For work celebration themes, use more specific searches
            services = [
                f"https://source.unsplash.com/{width}x{height}/?office,celebration,team,success",
                f"https://source.unsplash.com/{width}x{height}/?business,achievement,happy,workers",
                f"https://source.unsplash.com/{width}x{height}/?workplace,joy,colleagues,victory",
                f"https://picsum.photos/seed/workcelebration{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?corporate,party,professional,smile",
            ]
        elif theme == 'celebration':
            services = [
                f"https://source.unsplash.com/{width}x{height}/?celebration,party,happy,joy",
                f"https://source.unsplash.com/{width}x{height}/?success,achievement,victory,smile",
                f"https://source.unsplash.com/{width}x{height}/?festive,cheerful,positive,win",
                f"https://picsum.photos/seed/celebration{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?confetti,balloon,congratulation",
            ]
        elif theme == 'work':
            services = [
                f"https://source.unsplash.com/{width}x{height}/?workplace,professional,office,work",
                f"https://source.unsplash.com/{width}x{height}/?employees,team,collaboration,meeting",
                f"https://source.unsplash.com/{width}x{height}/?business,corporate,workers,desk",
                f"https://picsum.photos/seed/workplace{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?industry,labor,professional,job",
            ]
        elif theme == 'business':
            services = [
                f"https://source.unsplash.com/{width}x{height}/?business,office,professional,corporate",
                f"https://source.unsplash.com/{width}x{height}/?meeting,conference,handshake,deal",
                f"https://source.unsplash.com/{width}x{height}/?company,enterprise,boardroom,executive",
                f"https://picsum.photos/seed/business{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?finance,strategy,growth,success",
            ]
        elif theme == 'marketing':
            services = [
                f"https://source.unsplash.com/{width}x{height}/?marketing,advertising,communication,media",
                f"https://source.unsplash.com/{width}x{height}/?campaign,promotion,brand,digital",
                f"https://source.unsplash.com/{width}x{height}/?newsletter,email,social,content",
                f"https://picsum.photos/seed/marketing{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?publicity,outreach,engagement",
            ]
        elif theme == 'people':
            services = [
                f"https://source.unsplash.com/{width}x{height}/?people,group,crowd,community",
                f"https://source.unsplash.com/{width}x{height}/?person,individual,portrait,human",
                f"https://source.unsplash.com/{width}x{height}/?diverse,multicultural,team,unity",
                f"https://picsum.photos/seed/people{image_id}/{width}/{height}",
                f"https://source.unsplash.com/{width}x{height}/?faces,smile,positive,together",
            ]
        else:
            services = [
                f"https://source.unsplash.com/{width}x{height}/?{theme},professional,quality",
                f"https://picsum.photos/seed/{seed}{image_id}/{width}/{height}",
                f"https://via.placeholder.com/{width}x{height}/0891b2/ffffff?text={theme.title()}+Image"
            ]
        
        selected_url = random.choice(services)
        
        return {
            'url': selected_url,
            'prompt': prompt,
            'provider': self.id,
            'generated_at': 'now',
            'metadata': {
                'size': size,
                'seed': seed,
                'theme': theme,
                'service': 'placeholder',
                'detected_language': detected_language,
                'prompt_analysis': {
                    'has_celebration': any(word in prompt_lower for word in celebration_keywords),
                    'has_work': any(word in prompt_lower for word in work_keywords),
                    'has_business': any(word in prompt_lower for word in business_keywords),
                    'is_labor_day': any(keyword in prompt_lower for keyword in labor_day_keywords)
                }
            }
        }
    
    def is_available(self) -> bool:
        """Always available since it's a test provider"""
        return True
    
    def get_config_status(self) -> Dict[str, Any]:
        """Return configuration status"""
        return {
            'configured': True,
            'api_key_valid': True,
            'ready': True
        }

# Global instance
free_provider = FreeTestProvider()
