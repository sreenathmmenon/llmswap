from pathlib import Path
from typing import Optional


class LearningsTracker:
    
    def __init__(self, workspace_manager):
        self.workspace = workspace_manager
    
    def extract_and_save(self, query: str, response: str):
        learnings = self._extract_learnings(query, response)
        
        if learnings:
            self.workspace.append_learning(query, learnings)
    
    def _extract_learnings(self, query: str, response: str) -> Optional[str]:
        try:
            from llmswap.client import LLMClient
            
            extraction_prompt = f"""Extract 3-5 key learnings from this programming conversation.
Focus on:
- Concepts learned
- Best practices mentioned
- Actionable insights
- Technical decisions explained

Question: {query}

Answer: {response}

Provide learnings as bullet points (use - prefix).
Keep each point concise (1-2 sentences max).
If the conversation is just casual chat or doesn't have educational content, return "SKIP".
"""
            
            client = LLMClient(provider="groq", model="llama-3.1-8b-instant")
            result = client.query(extraction_prompt)
            
            if "SKIP" in result.content:
                return None
            
            return result.content
            
        except Exception as e:
            return None