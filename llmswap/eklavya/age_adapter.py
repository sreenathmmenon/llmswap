"""
Age-Appropriate Explanation System

Clean interface for age/audience/level-targeted explanations.
Let LLMs handle the intelligence, we handle the UX and prompt structure.
"""

from typing import Optional, Dict, Any


class AgeAdapter:
    """Handles age-appropriate explanation prompts"""
    
    @staticmethod
    def build_targeted_prompt(question: str, 
                            age: Optional[int] = None,
                            audience: Optional[str] = None,
                            level: Optional[str] = None,
                            explain_to: Optional[str] = None) -> str:
        """
        Build age/audience/level appropriate prompt.
        
        Args:
            question: The user's question
            age: Target age (e.g., 10, 25, 50)
            audience: Target audience (e.g., "business owner", "student")
            level: Knowledge level (beginner, intermediate, advanced)
            explain_to: Custom audience description
            
        Returns:
            Enhanced prompt for LLM
        """
        base_prompt = f"Question: {question}\n\n"
        
        # Age-based targeting
        if age:
            base_prompt += f"Explain this in a way that a {age}-year-old would understand. "
            base_prompt += "Use appropriate vocabulary, examples, and concepts for that age group. "
            
            # Add age-specific guidance
            if age <= 12:
                base_prompt += "Use simple words, fun examples, and maybe tell a short story to help explain. "
            elif age <= 18:
                base_prompt += "Use relatable examples from school, games, or everyday life. "
            elif age <= 30:
                base_prompt += "Focus on practical applications and career relevance. "
            elif age <= 50:
                base_prompt += "Emphasize practical value and real-world applications. "
            else:
                base_prompt += "Use patient explanations with clear analogies to familiar concepts. "
                
            base_prompt += "\n\n"
        
        # Audience-based targeting
        elif audience or explain_to:
            target_audience = audience or explain_to
            base_prompt += f"Explain this for: {target_audience}. "
            base_prompt += "Consider their background, interests, and likely knowledge level. "
            base_prompt += "Use examples and analogies that would resonate with them.\n\n"
        
        # Level-based targeting
        elif level:
            level_instructions = {
                'beginner': """Assume no prior knowledge of this topic. Start with the absolute basics and build up concepts step by step. 
Define any technical terms you use. Include simple examples to illustrate each point.""",
                
                'intermediate': """Assume some background knowledge in the general area. Focus on practical applications and how this connects to other concepts they might know. 
You can use some technical terms but explain complex ones.""",
                
                'advanced': """Assume strong foundation knowledge. Focus on depth, nuances, edge cases, and complex aspects. 
Discuss trade-offs, alternatives, and advanced considerations. Use appropriate technical terminology."""
            }
            base_prompt += level_instructions.get(level, level_instructions['intermediate'])
            base_prompt += "\n\n"
        
        base_prompt += "Provide a clear, helpful explanation that matches the specified audience."
        return base_prompt
    
    @staticmethod
    def get_context_info(age: Optional[int] = None,
                        audience: Optional[str] = None,
                        level: Optional[str] = None,
                        explain_to: Optional[str] = None) -> str:
        """Get display string for current context settings"""
        
        if age:
            return f"Age {age}"
        elif audience or explain_to:
            return f"{audience or explain_to}"
        elif level:
            return f"{level.title()} level"
        else:
            return "Standard"


class ChatContextManager:
    """Manages age/audience context in chat sessions"""
    
    def __init__(self):
        self.age = None
        self.audience = None
        self.level = None
        self.explain_to = None
    
    def set_age(self, age: int):
        """Set age context"""
        self.clear_all()
        self.age = age
    
    def set_audience(self, audience: str):
        """Set audience context"""
        self.clear_all()
        self.audience = audience
    
    def set_level(self, level: str):
        """Set knowledge level context"""
        self.clear_all()
        self.level = level
    
    def set_explain_to(self, explain_to: str):
        """Set custom explanation target"""
        self.clear_all()
        self.explain_to = explain_to
    
    def clear_all(self):
        """Clear all context settings"""
        self.age = None
        self.audience = None
        self.level = None
        self.explain_to = None
    
    def has_context(self) -> bool:
        """Check if any context is set"""
        return any([self.age, self.audience, self.level, self.explain_to])
    
    def get_context_display(self) -> str:
        """Get display string for current context"""
        return AgeAdapter.get_context_info(
            age=self.age,
            audience=self.audience,
            level=self.level,
            explain_to=self.explain_to
        )
    
    def enhance_question(self, question: str) -> str:
        """Enhance question with current context"""
        if not self.has_context():
            return question
            
        return AgeAdapter.build_targeted_prompt(
            question=question,
            age=self.age,
            audience=self.audience,
            level=self.level,
            explain_to=self.explain_to
        )


# Predefined audiences for common use cases
COMMON_AUDIENCES = {
    'child': 'a curious child',
    'student': 'a college student',
    'developer': 'a software developer',
    'manager': 'a business manager',
    'teacher': 'an educator',
    'parent': 'a parent',
    'senior': 'a senior citizen',
    'business-owner': 'a small business owner',
    'entrepreneur': 'an entrepreneur',
    'designer': 'a designer',
    'marketer': 'a marketing professional'
}


def get_audience_suggestions() -> Dict[str, str]:
    """Get common audience suggestions"""
    return COMMON_AUDIENCES