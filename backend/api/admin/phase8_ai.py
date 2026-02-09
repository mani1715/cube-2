"""
Phase 8.1A - AI Service Layer
AI-assisted admin tools using OpenAI GPT-4o-mini via emergentintegrations
"""
import os
from typing import Dict, List, Optional, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
import uuid

load_dotenv()

class AIBlogAssistant:
    """AI assistant for blog content generation and improvement"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    def _create_chat(self, system_message: str) -> LlmChat:
        """Create a new LLM chat instance"""
        session_id = f"blog-assistant-{uuid.uuid4()}"
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        # Use GPT-4o-mini for cost-effective, high-quality responses
        chat.with_model("openai", "gpt-4o-mini")
        return chat
    
    async def generate_draft(
        self, 
        topic: str, 
        keywords: Optional[List[str]] = None,
        tone: str = "professional",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a blog draft from a topic and keywords
        
        Args:
            topic: Main topic of the blog
            keywords: Optional list of keywords to include
            tone: Tone of the content (professional, casual, friendly)
            length: Length preference (short: ~300 words, medium: ~600 words, long: ~1000 words)
        
        Returns:
            Dict with title, content, and suggested tags
        """
        length_guidance = {
            "short": "approximately 300-400 words",
            "medium": "approximately 600-800 words",
            "long": "approximately 1000-1200 words"
        }
        
        keywords_text = f"\n- Keywords to include: {', '.join(keywords)}" if keywords else ""
        
        prompt = f"""Generate a complete blog post about: {topic}
        
- Tone: {tone}
- Length: {length_guidance.get(length, length_guidance['medium'])}{keywords_text}

Please provide:
1. An engaging title
2. Well-structured content with proper paragraphs
3. 3-5 relevant tags

Format your response as:
TITLE: [title here]

CONTENT:
[blog content here]

TAGS: [tag1, tag2, tag3, ...]"""
        
        system_message = """You are a professional content writer for a mental health and wellness platform called A-Cube. 
Create informative, empathetic, and engaging blog content. Focus on mental health awareness, wellness tips, 
psychological insights, and community support. Use clear language accessible to general audiences."""
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        # Parse the response
        return self._parse_blog_response(response)
    
    async def improve_content(
        self, 
        content: str, 
        improvement_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Improve existing blog content
        
        Args:
            content: The blog content to improve
            improvement_type: Type of improvement (general, clarity, engagement, tone)
        
        Returns:
            Dict with improved content and suggestions
        """
        improvement_instructions = {
            "general": "Improve overall quality, readability, and engagement",
            "clarity": "Make the content clearer and easier to understand",
            "engagement": "Make the content more engaging and compelling",
            "tone": "Adjust the tone to be more professional and empathetic"
        }
        
        instruction = improvement_instructions.get(improvement_type, improvement_instructions["general"])
        
        prompt = f"""Please improve the following blog content. Focus on: {instruction}

ORIGINAL CONTENT:
{content}

Provide the improved version maintaining the same general structure and key points, but enhancing quality."""
        
        system_message = """You are a professional content editor for a mental health platform. 
Improve content while maintaining its core message. Focus on clarity, engagement, and empathy."""
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        return {
            "improved_content": response.strip(),
            "improvement_type": improvement_type
        }
    
    async def suggest_tags(self, title: str, content: str) -> List[str]:
        """
        Suggest relevant tags for a blog post
        
        Args:
            title: Blog title
            content: Blog content
        
        Returns:
            List of suggested tags
        """
        prompt = f"""Based on this blog post, suggest 5-7 relevant tags/categories.

TITLE: {title}

CONTENT: {content[:500]}...

Provide only the tags as a comma-separated list, nothing else."""
        
        system_message = "You are a content categorization expert. Suggest relevant, specific tags."
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        # Parse tags
        tags = [tag.strip() for tag in response.split(",")]
        return tags[:7]  # Max 7 tags
    
    async def suggest_titles(self, content: str, count: int = 5) -> List[str]:
        """
        Suggest engaging titles for blog content
        
        Args:
            content: Blog content
            count: Number of title suggestions
        
        Returns:
            List of suggested titles
        """
        prompt = f"""Generate {count} engaging, clickable titles for this blog content:

{content[:600]}...

Provide titles as a numbered list, nothing else."""
        
        system_message = """You are a headline writing expert. Create compelling, clear titles 
that accurately represent the content and attract readers."""
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        # Parse titles
        titles = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                # Remove numbering/bullets
                title = line.lstrip("0123456789.-•) ").strip()
                if title:
                    titles.append(title)
        
        return titles[:count]
    
    async def generate_summary(self, content: str, max_length: int = 150) -> str:
        """
        Generate a concise summary of blog content
        
        Args:
            content: Blog content to summarize
            max_length: Maximum length of summary in words
        
        Returns:
            Summary text
        """
        prompt = f"""Create a concise, engaging summary of this blog post in approximately {max_length} words:

{content}

Provide only the summary, nothing else."""
        
        system_message = "You are a professional content summarizer. Create clear, engaging summaries."
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        return response.strip()
    
    async def quality_check(self, title: str, content: str) -> Dict[str, Any]:
        """
        Analyze content quality and provide feedback
        
        Args:
            title: Blog title
            content: Blog content
        
        Returns:
            Dict with quality scores and suggestions
        """
        word_count = len(content.split())
        
        prompt = f"""Analyze this blog post and provide quality feedback:

TITLE: {title}

CONTENT: {content}

Provide feedback in this format:
QUALITY_SCORE: [1-10]
READABILITY: [Easy/Medium/Hard]
TONE: [description]
STRENGTHS: [list 2-3 strengths]
IMPROVEMENTS: [list 2-3 suggestions]"""
        
        system_message = """You are a content quality analyst for a mental health platform. 
Provide constructive, specific feedback on content quality."""
        
        chat = self._create_chat(system_message)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        return {
            "word_count": word_count,
            "analysis": response.strip(),
            "estimated_read_time": max(1, round(word_count / 200))  # ~200 words per minute
        }
    
    def _parse_blog_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response for blog generation"""
        lines = response.split("\n")
        title = ""
        content = ""
        tags = []
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line_upper = line.upper().strip()
            
            if line_upper.startswith("TITLE:"):
                title = line[6:].strip()
                current_section = "title"
            elif line_upper.startswith("CONTENT:"):
                current_section = "content"
            elif line_upper.startswith("TAGS:"):
                tags_text = line[5:].strip()
                tags = [tag.strip() for tag in tags_text.split(",")]
                current_section = "tags"
            elif current_section == "content" and line.strip():
                content_lines.append(line)
        
        content = "\n".join(content_lines).strip()
        
        return {
            "title": title,
            "content": content,
            "suggested_tags": tags
        }


# Singleton instance
ai_assistant = AIBlogAssistant()
