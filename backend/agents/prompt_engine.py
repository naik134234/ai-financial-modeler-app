"""
Enterprise Financial Modeling Prompt Engine
Uses Claude/OpenRouter/Gemini API with industrial-grade prompts
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

# Try to import AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# OpenRouter/Claude configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class PromptEngine:
    """
    Enterprise-grade prompt engine for financial modeling.
    Implements the 9-step prompt chain for IB/PE-level models.
    """
    
    def __init__(self, provider: str = "claude"):
        self.provider = provider
        self.config_path = Path(__file__).parent.parent / "config"
        self.prompts = self._load_prompts()
        self.industry_prompts = self._load_industry_prompts()
        
        # Initialize AI client based on provider
        if provider == "claude":
            # Use OpenRouter for Claude API
            self.api_key = OPENROUTER_API_KEY
            self.model = "anthropic/claude-sonnet-4"  # Claude Sonnet 4
        elif provider == "gemini" and GEMINI_AVAILABLE:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            else:
                self.model = None
        elif provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.model = "gpt-4"
            else:
                self.model = None
        else:
            self.model = None

    
    def _load_prompts(self) -> Dict:
        """Load AI prompts configuration"""
        try:
            prompt_file = self.config_path / "ai_prompts.json"
            if prompt_file.exists():
                with open(prompt_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return self._get_default_prompts()
    
    def _load_industry_prompts(self) -> Dict:
        """Load industry-specific prompts"""
        try:
            industry_file = self.config_path / "industry_prompts.json"
            if industry_file.exists():
                with open(industry_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"industries": {}}
    
    def _get_default_prompts(self) -> Dict:
        """Default prompts if config not found"""
        return {
            "system_prompt": """You are an enterprise-grade Financial Modeling Engine used by 
Investment Banks, Private Equity funds, Consulting firms, and CFO offices.

You do NOT produce academic models.
You produce REAL-WORLD, AUDIT-READY, CLIENT-DELIVERABLE financial models.

DEFAULT ASSUMPTIONS:
- Conservative
- Explainable
- Defensible

STRICT RULES:
- No hardcoding except assumptions
- One calculation per row
- No broken links
- Full checks & balances

Proceed as a professional financial modeler.""",
            "prompt_chain": []
        }
    
    @property
    def system_prompt(self) -> str:
        """Get the master system prompt"""
        return self.prompts.get("system_prompt", "")
    
    def get_role_prompt(self, role: str) -> str:
        """
        Get role-specific prompt.
        
        Args:
            role: One of 'investment_banking', 'private_equity', 'fpa_cfo', 'model_auditor'
        """
        role_prompts = self.prompts.get("role_prompts", {})
        if role in role_prompts:
            return role_prompts[role].get("prompt", "")
        return ""
    
    def get_industry_context(self, industry: str) -> Dict:
        """
        Get industry-specific modeling context.
        
        Args:
            industry: One of 'banking', 'technology', 'manufacturing', 'fmcg', etc.
        """
        industries = self.industry_prompts.get("industries", {})
        return industries.get(industry, {})
    
    def build_modeling_prompt(
        self,
        company_name: str,
        industry: str,
        role: str = "investment_banking",
        step: str = "financial_statements",
        additional_context: Optional[str] = None
    ) -> str:
        """
        Build a complete modeling prompt for the AI.
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            role: Role perspective (IB, PE, CFO)
            step: Current step in the prompt chain
            additional_context: Any additional context
        
        Returns:
            Complete prompt string
        """
        parts = [self.system_prompt]
        
        # Add role context
        role_prompt = self.get_role_prompt(role)
        if role_prompt:
            parts.append(f"\n\n### ROLE CONTEXT\n{role_prompt}")
        
        # Add industry context
        industry_ctx = self.get_industry_context(industry)
        if industry_ctx:
            parts.append(f"\n\n### INDUSTRY: {industry_ctx.get('name', industry.upper())}")
            parts.append(f"Key Metrics: {', '.join(industry_ctx.get('key_metrics', []))}")
            parts.append(f"Revenue Drivers: {', '.join(industry_ctx.get('revenue_drivers', []))}")
            
            # Add specific prompts for the step
            specific = industry_ctx.get("specific_prompts", {})
            if step in specific:
                parts.append(f"\n{specific[step]}")
        
        # Add company context
        parts.append(f"\n\n### COMPANY: {company_name}")
        
        # Add step-specific prompt
        for chain_step in self.prompts.get("prompt_chain", []):
            if chain_step.get("id") == step:
                parts.append(f"\n\n### TASK: {chain_step.get('name', step.upper())}")
                parts.append(chain_step.get("prompt", ""))
                break
        
        # Add additional context
        if additional_context:
            parts.append(f"\n\n### ADDITIONAL CONTEXT\n{additional_context}")
        
        return "\n".join(parts)
    
    async def generate_assumptions(
        self,
        company_name: str,
        industry: str,
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate smart assumptions using AI.
        
        Args:
            company_name: Company name
            industry: Industry sector
            financial_data: Historical financial data
        
        Returns:
            Dictionary of recommended assumptions
        """
        if not self.model:
            return self._fallback_assumptions(industry)
        
        prompt = self.build_modeling_prompt(
            company_name=company_name,
            industry=industry,
            role="private_equity",
            step="business_understanding",
            additional_context=f"Financial Data:\n{json.dumps(financial_data, indent=2)}"
        )
        
        response_prompt = """
Based on the above, provide assumptions in this EXACT JSON format:
{
    "revenue_growth": 0.10,
    "ebitda_margin": 0.20,
    "terminal_growth": 0.03,
    "wacc": 0.12,
    "tax_rate": 0.25,
    "capex_percent": 0.05,
    "working_capital_days": 45,
    "depreciation_rate": 0.10,
    "rationale": "Brief explanation of key assumptions"
}
Return ONLY valid JSON, no other text.
"""
        
        full_prompt = prompt + "\n\n" + response_prompt
        
        try:
            if self.provider == "claude":
                # Call Claude via OpenRouter
                response = requests.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai-financial-modeler.com",
                        "X-Title": "AI Financial Modeler"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": full_prompt}
                        ]
                    }
                )
                result_text = response.json()["choices"][0]["message"]["content"]
            elif self.provider == "gemini" and GEMINI_AVAILABLE:
                response = self.model.generate_content(full_prompt)
                result_text = response.text
            elif self.provider == "openai" and OPENAI_AVAILABLE:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                result_text = response.choices[0].message.content
            else:
                return self._fallback_assumptions(industry)
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"AI assumption generation failed: {e}")
        
        return self._fallback_assumptions(industry)
    
    def _fallback_assumptions(self, industry: str) -> Dict[str, Any]:
        """Fallback assumptions when AI is unavailable"""
        industry_defaults = {
            "banking": {"revenue_growth": 0.12, "ebitda_margin": 0.35, "wacc": 0.13},
            "technology": {"revenue_growth": 0.20, "ebitda_margin": 0.25, "wacc": 0.12},
            "manufacturing": {"revenue_growth": 0.08, "ebitda_margin": 0.15, "wacc": 0.11},
            "fmcg": {"revenue_growth": 0.10, "ebitda_margin": 0.18, "wacc": 0.10},
            "pharma": {"revenue_growth": 0.12, "ebitda_margin": 0.22, "wacc": 0.11},
            "power_utilities": {"revenue_growth": 0.05, "ebitda_margin": 0.30, "wacc": 0.09},
        }
        
        base = {
            "revenue_growth": 0.10,
            "ebitda_margin": 0.18,
            "terminal_growth": 0.04,
            "wacc": 0.12,
            "tax_rate": 0.25,
            "capex_percent": 0.05,
            "working_capital_days": 45,
            "depreciation_rate": 0.10,
            "rationale": "Industry-standard conservative assumptions"
        }
        
        if industry in industry_defaults:
            base.update(industry_defaults[industry])
        
        return base
    
    def validate_model(self, model_data: Dict) -> Dict[str, Any]:
        """
        Validate model using audit checklist.
        
        Returns validation results with any issues found.
        """
        validation_checks = self.prompts.get("validation_checks", [])
        
        issues = []
        warnings = []
        
        # Check balance sheet
        if "balance_sheet" in model_data:
            bs = model_data["balance_sheet"]
            assets = bs.get("total_assets", 0)
            liab_equity = bs.get("total_liabilities", 0) + bs.get("total_equity", 0)
            if abs(assets - liab_equity) > 0.01:
                issues.append("Balance sheet does not balance")
        
        # Check for reasonable assumptions
        assumptions = model_data.get("assumptions", {})
        if assumptions.get("revenue_growth", 0) > 0.50:
            warnings.append("Revenue growth > 50% - validate with management")
        if assumptions.get("ebitda_margin", 0) > 0.60:
            warnings.append("EBITDA margin > 60% - unusual for most industries")
        if assumptions.get("terminal_growth", 0) > 0.05:
            warnings.append("Terminal growth > 5% - exceeds long-term GDP growth")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "checks_performed": validation_checks
        }
    
    def get_excel_standards(self) -> Dict:
        """Get Excel formatting standards"""
        return self.prompts.get("excel_standards", {
            "colors": {
                "inputs": "blue",
                "formulas": "black",
                "links": "green",
                "errors": "red",
                "headers": "grey"
            },
            "rules": [
                "One sheet per function",
                "No merged cells",
                "Consistent timeline"
            ]
        })


# Singleton instance
_engine = None

def get_prompt_engine(provider: str = "claude") -> PromptEngine:
    """Get or create the prompt engine instance"""
    global _engine
    if _engine is None:
        _engine = PromptEngine(provider)
    return _engine
