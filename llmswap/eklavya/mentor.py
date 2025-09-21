"""
EklavyaMentor - Core mentorship class

Provides personalized AI mentorship with adaptive personas and learning tracking.
"""

import os
import yaml
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from .personas import PERSONAS, get_persona_prompt, get_persona_style, list_available_personas


class EklavyaMentor:
    """
    Core mentorship class providing personalized AI teaching and guidance.
    
    Features:
    - Multiple teaching personas (guru, coach, friend, etc.)
    - Custom mentor aliases (name your mentor)
    - Learning progress tracking
    - Emotional intelligence
    - Adaptive teaching styles
    """
    
    def __init__(self, 
                 persona: str = 'guru',
                 alias: Optional[str] = None,
                 learner_name: Optional[str] = None):
        """
        Initialize Eklavya mentor.
        
        Args:
            persona: Teaching persona (guru, coach, friend, etc.)
            alias: Custom name for the mentor
            learner_name: Name of the learner
        """
        self.persona = persona if persona in PERSONAS else 'guru'
        self.alias = alias or PERSONAS[self.persona]['default_alias']
        self.learner_name = learner_name or "Student"
        
        # Learning tracking
        self.session_start_time = time.time()
        self.topics_discussed = []
        self.learning_goals = []
        self.session_interactions = 0
        
        # Emotional intelligence
        self.detected_mood = "neutral"
        self.last_interaction_sentiment = "neutral"
        
        # Configuration
        self.config_dir = Path.home() / '.llmswap' / 'eklavya'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create learner profile
        self.profile = self._load_learner_profile()
        
    def enhance_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Enhance user prompt with mentorship context.
        
        Args:
            user_input: Original user input
            context: Additional context for the conversation
            
        Returns:
            Enhanced prompt with mentorship context
        """
        # Detect emotional state
        self.detected_mood = self._detect_mood(user_input)
        
        # Track topics being discussed
        self._update_learning_context(user_input)
        
        # Get persona-specific system prompt
        persona_prompt = get_persona_prompt(self.persona, self.alias)
        
        # Build comprehensive context
        mentor_context = self._build_mentor_context()
        
        # Create enhanced prompt
        enhanced_prompt = f"""
{persona_prompt}

CURRENT CONTEXT:
{mentor_context}

STUDENT'S MESSAGE: {user_input}

RESPONSE INSTRUCTIONS:
- Respond as {self.alias} ({self.persona} mentor)
- Consider the student's emotional state: {self.detected_mood}
- Adapt your response to their learning style and current mood
- Be helpful, encouraging, and true to your persona
- If asked about learning progress, reference the topics discussed this session
"""
        
        self.session_interactions += 1
        return enhanced_prompt
    
    def _build_mentor_context(self) -> str:
        """Build comprehensive context for the mentor."""
        duration = int(time.time() - self.session_start_time)
        minutes = duration // 60
        
        context_parts = [
            f"Student Name: {self.learner_name}",
            f"Session Duration: {minutes} minutes",
            f"Interactions This Session: {self.session_interactions}",
            f"Student's Current Mood: {self.detected_mood}"
        ]
        
        if self.topics_discussed:
            recent_topics = self.topics_discussed[-3:]  # Last 3 topics
            context_parts.append(f"Recent Topics: {', '.join(recent_topics)}")
        
        if self.learning_goals:
            context_parts.append(f"Learning Goals: {', '.join(self.learning_goals)}")
        
        # Add profile information
        if self.profile:
            level = self.profile.get('level', 'intermediate')
            interests = self.profile.get('interests', [])
            context_parts.append(f"Skill Level: {level}")
            if interests:
                context_parts.append(f"Interests: {', '.join(interests)}")
        
        return "\n".join(context_parts)
    
    def _detect_mood(self, text: str) -> str:
        """
        Simple mood detection based on keywords and patterns.
        
        Args:
            text: User input text
            
        Returns:
            Detected mood string
        """
        text_lower = text.lower()
        
        # Frustration indicators
        if any(word in text_lower for word in ['stuck', 'frustrated', 'annoying', "can't", 'impossible', 'difficult', 'hard']):
            return "frustrated"
        
        # Confusion indicators
        if any(word in text_lower for word in ['confused', "don't understand", 'unclear', 'what', 'how', '?']):
            return "confused"
        
        # Excitement indicators
        if any(word in text_lower for word in ['awesome', 'great', 'love', 'amazing', 'excellent', 'fantastic']):
            return "excited"
        
        # Tired/exhausted indicators
        if any(word in text_lower for word in ['tired', 'exhausted', 'long day', 'overwhelmed']):
            return "tired"
        
        # Determined indicators
        if any(word in text_lower for word in ['will', 'must', 'going to', 'determined', 'goal']):
            return "determined"
        
        # Grateful indicators
        if any(word in text_lower for word in ['thank', 'thanks', 'grateful', 'appreciate']):
            return "grateful"
        
        return "neutral"
    
    def _update_learning_context(self, user_input: str):
        """Update learning context based on user input."""
        # Simple topic extraction (can be enhanced with NLP)
        common_topics = {
            'python': ['python', 'py', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue'],
            'algorithms': ['algorithm', 'sorting', 'searching', 'big o', 'complexity'],
            'data structures': ['array', 'list', 'tree', 'graph', 'stack', 'queue'],
            'databases': ['database', 'sql', 'mysql', 'postgres', 'mongodb'],
            'web development': ['html', 'css', 'web', 'frontend', 'backend'],
            'machine learning': ['ml', 'machine learning', 'ai', 'neural', 'model'],
            'system design': ['system design', 'architecture', 'scalability', 'microservices']
        }
        
        input_lower = user_input.lower()
        for topic, keywords in common_topics.items():
            if any(keyword in input_lower for keyword in keywords):
                if topic not in self.topics_discussed:
                    self.topics_discussed.append(topic)
                break
    
    def _load_learner_profile(self) -> Dict[str, Any]:
        """Load learner profile from configuration file."""
        profile_file = self.config_dir / 'profile.yaml'
        
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # Create default profile
        default_profile = {
            'name': self.learner_name,
            'level': 'intermediate',
            'interests': [],
            'goals': [],
            'learning_style': 'balanced',
            'created_at': time.time()
        }
        
        self._save_learner_profile(default_profile)
        return default_profile
    
    def _save_learner_profile(self, profile: Dict[str, Any]):
        """Save learner profile to configuration file."""
        profile_file = self.config_dir / 'profile.yaml'
        
        try:
            with open(profile_file, 'w') as f:
                yaml.dump(profile, f, default_flow_style=False)
        except Exception:
            pass  # Fail silently for now
    
    def switch_persona(self, new_persona: str) -> bool:
        """
        Switch to a different mentorship persona.
        
        Args:
            new_persona: Name of the new persona
            
        Returns:
            True if switch successful, False otherwise
        """
        if new_persona in PERSONAS:
            self.persona = new_persona
            # Update alias to default for new persona if not customized
            if self.alias == PERSONAS.get(self.persona, {}).get('default_alias'):
                self.alias = PERSONAS[new_persona]['default_alias']
            return True
        return False
    
    def set_alias(self, new_alias: str):
        """Set custom alias for the mentor."""
        if new_alias and new_alias.strip():
            self.alias = new_alias.strip()
    
    def set_learner_name(self, name: str):
        """Set the learner's name."""
        if name and name.strip():
            self.learner_name = name.strip()
            self.profile['name'] = self.learner_name
            self._save_learner_profile(self.profile)
    
    def add_learning_goal(self, goal: str):
        """Add a learning goal."""
        if goal and goal.strip():
            goal = goal.strip()
            if goal not in self.learning_goals:
                self.learning_goals.append(goal)
                
                # Also save to profile
                if 'goals' not in self.profile:
                    self.profile['goals'] = []
                if goal not in self.profile['goals']:
                    self.profile['goals'].append(goal)
                    self._save_learner_profile(self.profile)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current learning session."""
        duration = int(time.time() - self.session_start_time)
        minutes = duration // 60
        
        return {
            'mentor_name': self.alias,
            'mentor_persona': self.persona,
            'learner_name': self.learner_name,
            'session_duration_minutes': minutes,
            'interactions': self.session_interactions,
            'topics_discussed': self.topics_discussed,
            'current_mood': self.detected_mood,
            'learning_goals': self.learning_goals
        }
    
    def get_available_personas(self) -> Dict[str, str]:
        """Get list of available personas with descriptions."""
        return list_available_personas()
    
    def get_motivation_message(self) -> str:
        """Get a motivational message based on current persona."""
        persona_style = get_persona_style(self.persona)
        
        messages = {
            'guru': f"Remember, dear {self.learner_name}, like a river that cuts through rock not by force but by persistence, your learning journey requires patience and dedication. Each question you ask brings you closer to wisdom.",
            
            'coach': f"Hey {self.learner_name}! You're doing amazing! 💪 Every challenge is just another opportunity to level up. Remember, champions are made when nobody's watching. Keep pushing - you've got this! 🔥",
            
            'friend': f"Hey {self.learner_name}, I just want you to know that you're making real progress! Learning can be tough sometimes, but you're handling it really well. We're in this together, and I'm here whenever you need support! 😊",
            
            'socrates': f"Tell me, {self.learner_name}, what have you discovered about yourself as a learner today? What questions arise in your mind that weren't there before? Remember, the unexamined learning is not worth pursuing.",
            
            'sensei': f"{self.learner_name}, your dedication to learning honors the path of mastery. Like bamboo that bends but does not break, flexibility in learning makes you stronger. Continue your practice with discipline and patience."
        }
        
        return messages.get(self.persona, messages['guru'])
    
    def handle_mentor_command(self, command: str) -> str:
        """
        Handle mentor-specific commands.
        
        Args:
            command: Command string (without the leading /)
            
        Returns:
            Response message
        """
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'motivate':
            return self.get_motivation_message()
        
        elif cmd == 'progress':
            summary = self.get_session_summary()
            response = f"📊 **Learning Progress for {summary['learner_name']}**\n\n"
            response += f"🧘 Mentor: {summary['mentor_name']} ({summary['mentor_persona']})\n"
            response += f"⏱️ Session Duration: {summary['session_duration_minutes']} minutes\n"
            response += f"💬 Interactions: {summary['interactions']}\n"
            response += f"😊 Current Mood: {summary['current_mood']}\n\n"
            
            if summary['topics_discussed']:
                response += f"📚 Topics Discussed: {', '.join(summary['topics_discussed'])}\n"
            
            if summary['learning_goals']:
                response += f"🎯 Learning Goals: {', '.join(summary['learning_goals'])}\n"
            
            return response
        
        elif cmd == 'alias' and len(parts) > 1:
            new_alias = ' '.join(parts[1:])
            self.set_alias(new_alias)
            return f"✅ Your mentor is now called '{self.alias}'"
        
        elif cmd == 'mentor' and len(parts) > 1:
            new_persona = parts[1].lower()
            if self.switch_persona(new_persona):
                return f"✅ Switched to {new_persona} mode. Your mentor {self.alias} is ready to help in their new role!"
            else:
                available = ', '.join(self.get_available_personas().keys())
                return f"❌ Unknown persona '{new_persona}'. Available: {available}"
        
        elif cmd == 'goal' and len(parts) > 1:
            goal = ' '.join(parts[1:])
            self.add_learning_goal(goal)
            return f"🎯 Added learning goal: '{goal}'"
        
        elif cmd == 'personas':
            personas = self.get_available_personas()
            response = "🎭 **Available Mentor Personas:**\n\n"
            for persona, description in personas.items():
                current = " (current)" if persona == self.persona else ""
                response += f"**{persona}**{current}: {description}\n"
            return response
        
        else:
            return f"❌ Unknown mentor command: /{cmd}. Try /motivate, /progress, /personas, /alias <name>, /mentor <persona>, or /goal <goal>"