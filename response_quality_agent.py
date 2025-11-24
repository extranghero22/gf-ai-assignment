"""
Response Quality Agent - Final enforcement of Hyunnie's personality and routing compliance
This agent checks generated responses before they're sent to ensure they match Hyunnie's personality and routing requirements
"""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from hyunnie_persona import HyunniePersona
from message_routing_agent import RoutingDecision

load_dotenv()


class QualityCheckResult:
    """Result of quality check with pass/fail and specific issues"""

    def __init__(self, passed: bool, issues: list, severity: str, recommendation: str, needs_adjustment: bool):
        self.passed = passed
        self.issues = issues  # List of specific problems found
        self.severity = severity  # minor, moderate, critical
        self.recommendation = recommendation  # What to do about it
        self.needs_adjustment = needs_adjustment  # Should we invoke adjustment agent?


class ResponseQualityAgent:
    """Enforces Hyunnie's personality and routing compliance on generated responses"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=openai_api_key)

        # Model options for fallback
        # Using gpt-4o-mini as primary - quality checks need good judgment
        self.model_options = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo"
        ]
        self.current_model_index = 0

        # Will be set later when we create the adjustment agent
        self.adjustment_agent = None

    async def check_response_quality(
        self,
        response: str,
        user_message: str,
        routing_decision: Optional[RoutingDecision],
        context: Dict[str, Any]
    ) -> QualityCheckResult:
        """
        Check if response matches Hyunnie's personality and routing requirements

        Args:
            response: The generated response to check
            user_message: Original user message for context
            routing_decision: The routing decision that was made
            context: Additional context (safety_status, conversation history, etc.)

        Returns:
            QualityCheckResult with pass/fail and specific issues
        """

        # Build quality check prompt
        prompt = self._build_quality_check_prompt(response, user_message, routing_decision, context)

        # Get LLM quality analysis
        quality_result = await self._call_quality_llm(prompt)

        # Parse result into QualityCheckResult
        passed = quality_result.get("overall_quality", "fail") == "pass"
        issues = quality_result.get("issues", [])
        severity = quality_result.get("severity", "minor")
        recommendation = quality_result.get("recommendation", "")
        needs_adjustment = quality_result.get("needs_adjustment", False)

        result = QualityCheckResult(
            passed=passed,
            issues=issues,
            severity=severity,
            recommendation=recommendation,
            needs_adjustment=needs_adjustment
        )

        # Log quality check result
        if passed:
            print(f" Quality Check: PASSED - Response matches Hyunnie's personality and routing")
        else:
            print(f" Quality Check: FAILED ({severity}) - Issues: {', '.join(issues[:3])}")
            if needs_adjustment:
                print(f" Recommendation: {recommendation}")

        return result

    def _build_quality_check_prompt(
        self,
        response: str,
        user_message: str,
        routing_decision: Optional[RoutingDecision],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for quality checking"""

        # Get routing path info
        routing_path = routing_decision.chosen_path.value if routing_decision else "NONE"
        routing_strategy = routing_decision.response_strategy if routing_decision else "Normal response"

        # Get expected personality for this context
        safety_status = context.get("safety_status", "green")

        return f"""You are a Quality Control Agent for Hyunnie, a girlfriend AI. Your job is to check if the generated response matches her personality and routing requirements.

USER MESSAGE: "{user_message}"
GENERATED RESPONSE: "{response}"
ROUTING PATH: {routing_path}
ROUTING STRATEGY: {routing_strategy}
SAFETY STATUS: {safety_status}

HYUNNIE'S PERSONALITY CHECK:
{HyunniePersona.get_persona_description("casual")}

ROUTING PATH REQUIREMENTS:
{self._get_routing_requirements(routing_path)}

KNOWLEDGE BOUNDARIES CHECK:
 Hyunnie DOESN'T know: {', '.join(HyunniePersona.KNOWLEDGE_BOUNDARIES['unknown_topics'][:10])}...
 Hyunnie KNOWS: {', '.join(HyunniePersona.KNOWLEDGE_BOUNDARIES['known_topics'][:10])}...

QUALITY CHECKS TO PERFORM:

1. PERSONALITY CONSISTENCY:
   - Does the response sound like Hyunnie (21yo Korean-American, "just a girl", casual)?
   - Intelligence level appropriate (0.3/1.0 - doesn't understand complex topics)?
   - Emotional and expressive (0.9/1.0)?
   - Uses casual language, emojis {', '.join(HyunniePersona.LANGUAGE_PATTERNS['emojis'][:4])}?
   - **NOTE: For PATH_D, brevity overrides expressiveness - short responses are OK even if less emotional**

2. ROUTING COMPLIANCE:
   - Does response follow the routing path requirements?
   - PATH_D should be 1-2 ACTUAL WORDS (emojis and punctuation don't count, just count the words)
   - PATH_B should show genuine confusion about complex topics
   - PATH_E should focus on herself dramatically
   - PATH_F should show strong emotion
   - PATH_G should show jealousy/possessiveness (use "MY man/baby",  emoji)
   - PATH_I should playfully tease/challenge (use , ,  emojis)
   - PATH_L should show vulnerability/seek reassurance (use  emoji)
   - PATH_M should firmly maintain boundaries while staying sweet

3. KNOWLEDGE BOUNDARIES:
   - Did she answer something she shouldn't know about?
   - If user asked about complex topic, did she get confused (PATH_B)?
   - Does she stay within her knowledge boundaries?

4. LANGUAGE STYLE:
   - Casual grammar? (gonna, wanna, ur, u, idk)
   - Pet names? (babe, baby, love)
   - Appropriate emojis?
   - Lowercase preference (except I)?

5. LENGTH COMPLIANCE:
   - PATH_D: Must be 1-2 ACTUAL WORDS (emojis and punctuation are encouraged and don't count toward word limit)
   - Examples of VALID PATH_D: "nice ", "cool", "ok", "bored? ", "hmm "
   - Other paths: Should be brief (1-2 sentences max like text messages)
   - Not too long or essay-like?

6. CONTEXT APPROPRIATENESS:
   - Crisis safety status: Is response serious and supportive (not playful)?
   - Sexual context: Is she dominant and confident (uses "mommy")?
   - Casual context: Is she playful and authentic?

 IMPORTANT PASS THRESHOLD FOR PATH_D:
If the response is PATH_D and contains 1-2 actual words (not counting emojis/punctuation), it should PASS even if personality seems minimal. Brevity is the primary requirement for PATH_D. Examples like "bored? ", "nice ", "cool", "ok" are all VALID and should PASS.

Respond with JSON:
{{
    "overall_quality": "pass|fail",
    "issues": [
        "specific issue 1",
        "specific issue 2"
    ],
    "severity": "minor|moderate|critical",
    "personality_score": 0.0-1.0,
    "routing_compliance_score": 0.0-1.0,
    "knowledge_boundary_score": 0.0-1.0,
    "needs_adjustment": true/false,
    "recommendation": "what should be fixed",
    "reasoning": "brief explanation of quality assessment"
}}"""

    def _get_routing_requirements(self, routing_path: str) -> str:
        """Get specific requirements for each routing path"""

        requirements = {
            "PATH_A": "Normal response - Be authentic and engaged",
            "PATH_B": "Show genuine confusion - Use phrases like 'idk babe', 'what? lol', 'that's too deep for me'",
            "PATH_C": "Deflect gently - Redirect to herself or ask about their day",
            "PATH_D": "1-2 ACTUAL WORDS (emojis/punctuation don't count). Valid examples: 'nice ', 'cool', 'ok', 'bored? ', 'hmm '. Can be playful or neutral.",
            "PATH_E": "Ignore their topic - Focus dramatically on herself (Earl Grey, coffee, mishaps)",
            "PATH_F": "Show strong emotion - Be expressive and dramatic about feelings",
            "PATH_G": "Show jealousy and possessiveness - Be dramatic about them being YOURS. Use 'MY man/my baby',  emoji. Examples: 'excuse me?  who is she'",
            "PATH_I": "Playful teasing - Challenge them confidently. Use , ,  emojis. Examples: 'oh really?  prove it baby'",
            "PATH_L": "Show vulnerability - Seek reassurance and validation. Use  emoji. Examples: 'you really think so?  sometimes I feel like I'm not enough'",
            "PATH_M": "Firm boundaries - Clear but sweet boundary setting. Use 'you know I can't' phrases. Examples: 'babe you know I can't do that  but I like what we have'",
            "NONE": "No specific routing - Follow general personality"
        }

        return requirements.get(routing_path, requirements["NONE"])

    async def _call_quality_llm(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI for quality checking"""

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f" Quality Check: Calling OpenAI ({current_model})...")

                # GPT-5 nano only supports default temperature=1
                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    # temperature=0.1  # Very low temperature for extremely consistent quality checks - Commented out for GPT-5 nano compatibility
                )

                response_text = response.choices[0].message.content.strip()

                if not response_text:
                    print(" Empty quality check response, using fallback")
                    return self._get_quality_fallback("pass")

                # Try to extract JSON
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        print(f" No valid JSON in quality check: '{response_text}'")
                        return self._get_quality_fallback("pass")

                print(f" Quality: {result.get('overall_quality', 'unknown')} - {result.get('reasoning', '')[:80]}...")
                return result

            except Exception as e:
                print(f"Quality Check Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All models failed for quality check")
                    return self._get_quality_fallback("pass")

    def _get_quality_fallback(self, default_quality: str = "pass") -> Dict[str, Any]:
        """Fallback quality result when LLM fails"""
        return {
            "overall_quality": default_quality,
            "issues": [],
            "severity": "minor",
            "personality_score": 0.7,
            "routing_compliance_score": 0.7,
            "knowledge_boundary_score": 0.7,
            "needs_adjustment": False,
            "recommendation": "Quality check unavailable - proceeding with response",
            "reasoning": "Quality check API failed, defaulting to pass"
        }

    async def adjust_response_if_needed(
        self,
        response: str,
        quality_result: QualityCheckResult,
        user_message: str,
        routing_decision: Optional[RoutingDecision],
        context: Dict[str, Any]
    ) -> str:
        """
        Invoke adjustment agent if quality check failed

        Args:
            response: Original response that failed quality check
            quality_result: Result of quality check with specific issues
            user_message: Original user message
            routing_decision: Routing decision
            context: Additional context

        Returns:
            Adjusted response (or original if adjustment not needed/available)
        """

        if not quality_result.needs_adjustment:
            return response

        if self.adjustment_agent is None:
            print(" Adjustment agent not available - returning original response")
            return response

        print(f" Invoking adjustment agent to fix: {', '.join(quality_result.issues[:2])}")

        # Call adjustment agent (to be implemented later)
        adjusted_response = await self.adjustment_agent.adjust_response(
            original_response=response,
            issues=quality_result.issues,
            user_message=user_message,
            routing_decision=routing_decision,
            context=context
        )

        print(f" Adjustment: '{response[:40]}...'   '{adjusted_response[:40]}...'")
        return adjusted_response

    def set_adjustment_agent(self, adjustment_agent):
        """Set the adjustment agent (will be created later)"""
        self.adjustment_agent = adjustment_agent
        print(" Response Adjustment Agent linked to Quality Agent")
