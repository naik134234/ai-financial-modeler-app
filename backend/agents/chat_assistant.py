"""
AI Chat Assistant
Interactive chat for model Q&A and what-if scenarios
Uses Claude API via OpenRouter
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class ChatAssistant:
    """AI-powered chat assistant for financial model Q&A"""
    
    def __init__(self, model: str = "anthropic/claude-3-haiku"):
        self.model = model
        self.api_key = OPENROUTER_API_KEY or ""
        self.conversation_history: List[Dict] = []
    
    def create_model_context(self, job_data: Dict) -> str:
        """Create context string from job data for the AI"""
        company = job_data.get('company_name', 'Unknown Company')
        industry = job_data.get('industry', 'general')
        assumptions = job_data.get('assumptions', {})
        valuation = job_data.get('valuation_data', {})
        
        context = f"""You are analyzing a financial model for {company} ({industry} sector).

KEY ASSUMPTIONS:
- Revenue Growth: {assumptions.get('revenue_growth', 'N/A')}
- EBITDA Margin: {assumptions.get('ebitda_margin', 'N/A')}
- WACC: {assumptions.get('wacc', 'N/A')}
- Terminal Growth: {assumptions.get('terminal_growth', 'N/A')}
- Tax Rate: {assumptions.get('tax_rate', 'N/A')}

VALUATION METRICS:
- Enterprise Value: ₹{valuation.get('enterprise_value', 'N/A'):,.0f} Cr
- Equity Value: ₹{valuation.get('equity_value', 'N/A'):,.0f} Cr
- Implied Share Price: ₹{valuation.get('share_price', 'N/A'):,.2f}
- Current Market Price: ₹{valuation.get('current_price', 'N/A'):,.2f}

COMPANY FINANCIALS:
- Revenue: ₹{assumptions.get('base_revenue', 'N/A'):,.0f} Cr
- EBITDA: ₹{assumptions.get('base_ebitda', 'N/A'):,.0f} Cr
- Net Debt: ₹{valuation.get('net_debt', 'N/A'):,.0f} Cr

You are a helpful financial analyst assistant. Answer questions about this model concisely.
When discussing valuation, explain the key drivers and risks.
For what-if scenarios, estimate the directional impact on valuation."""
        
        return context
    
    def chat(
        self, 
        message: str, 
        job_data: Dict,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message and get AI response
        
        Args:
            message: User's question
            job_data: Current model data for context
            chat_history: Previous messages in conversation
        
        Returns:
            AI response with metadata
        """
        try:
            context = self.create_model_context(job_data)
            
            messages = [{"role": "system", "content": context}]
            
            # Add chat history
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result['choices'][0]['message']['content']
                
                return {
                    "success": True,
                    "response": ai_message,
                    "model": self.model,
                    "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                }
            else:
                logger.error(f"Chat API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "response": "I'm having trouble connecting. Please try again.",
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def suggest_questions(self, job_data: Dict) -> List[str]:
        """Generate suggested questions based on the model"""
        company = job_data.get('company_name', 'the company')
        valuation = job_data.get('valuation_data', {})
        
        share_price = valuation.get('share_price', 0)
        current_price = valuation.get('current_price', 0)
        
        suggestions = [
            f"What are the key value drivers for {company}?",
            "What are the main risks to this valuation?",
            "How sensitive is the valuation to WACC changes?",
            "What would happen if revenue growth dropped to 5%?",
        ]
        
        if share_price > current_price:
            suggestions.append("Why is the model showing upside potential?")
        else:
            suggestions.append("Why is the current price above intrinsic value?")
        
        return suggestions


# Singleton instance
chat_assistant = ChatAssistant()


def process_chat_message(message: str, job_data: Dict, history: List = None) -> Dict:
    """Main entry point for chat processing"""
    return chat_assistant.chat(message, job_data, history)


def get_suggested_questions(job_data: Dict) -> List[str]:
    """Get AI-generated question suggestions"""
    return chat_assistant.suggest_questions(job_data)
