"""
Eklavya Mentorship Mode - Transform any AI into your personal mentor

Named after the legendary archer Eklavya, this module provides:
- Personalized AI mentorship
- Multiple teaching personas
- Adaptive learning tracking
- Emotional intelligence
- Custom mentor relationships

Usage:
    from llmswap.eklavya import EklavyaMentor
    
    mentor = EklavyaMentor(persona='guru', alias='Guruji')
    enhanced_prompt = mentor.enhance_prompt("How do I learn Python?")
"""

from .mentor import EklavyaMentor
from .personas import PERSONAS, MentorPersona

__all__ = ['EklavyaMentor', 'PERSONAS', 'MentorPersona']