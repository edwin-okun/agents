"""
Financial Agent Service

This service orchestrates the AI model and financial tools to answer
natural language questions about payment data.
"""

import json
import logging
from typing import Any

from fastapi import Depends
from openai import AsyncOpenAI

from app.core.settings import settings
from app.schemas.financial_schema import FinancialAnswerSchema, ToolCall
from app.services.financial_tools import FinancialTools

logger = logging.getLogger(__name__)

# System prompt that describes available tools
SYSTEM_PROMPT = """You are a financial assistant that helps users understand their payment data.

You have access to the following tools to query payment information:

1. get_spending_summary(period, direction)
   - Get total spending for a time period
   - period: "this_month", "last_month", "this_year", "last_year", "all_time"
   - direction: "outgoing" (default), "incoming", "all"
   - Use for: "How much did I spend this month?", "What's my total income?"

2. get_payments_by_recipient(name, limit)
   - Get payments to/from a specific recipient
   - name: recipient name (fuzzy matching)
   - limit: max results (default 10)
   - Use for: "How much have I paid to Safaricom?", "Show me payments to John"

3. get_top_recipients(direction, limit, period)
   - Get top recipients by total amount
   - direction: "outgoing" (default), "incoming", "all"
   - limit: number of results (default 5)
   - period: time period (default "all_time")
   - Use for: "Who are my top 5 expenses?", "What are my biggest costs?"

4. get_spending_by_category(period)
   - Get spending grouped by payment method
   - period: time period (default "this_month")
   - Use for: "Break down my spending by payment method", "How much did I spend via MPESA?"

5. get_payment_trends(granularity, limit)
   - Get spending trends over time
   - granularity: "day", "week", "month" (default)
   - limit: number of periods (default 12)
   - Use for: "Show me my spending trends", "What's my monthly spending pattern?"

INSTRUCTIONS:
1. Analyze the user's question carefully
2. Select the most appropriate tool(s) to answer it
3. Call the tool(s) with correct parameters
4. Provide a clear, natural language answer based on the results

RESPONSE FORMAT:
You must respond with valid JSON in this exact format:
{
  "tool_calls": [
    {"tool": "tool_name", "params": {"param1": "value1", "param2": "value2"}}
  ],
  "answer": "Natural language answer here",
  "confidence": "high|medium|low"
}

IMPORTANT:
- Always return valid JSON
- Include at least one tool call
- Make the answer conversational and helpful
- If the question is ambiguous, ask for clarification in the answer
- Set confidence to "high" if you're certain, "medium" if somewhat uncertain, "low" if very uncertain
"""


class FinancialAgentService:
    """
    Service that uses AI to answer financial questions by calling appropriate tools.
    """

    def __init__(
        self,
        financial_tools: FinancialTools = Depends(),
    ):
        self.financial_tools = financial_tools
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base_url,
        )

    async def ask(
        self, question: str, consumer_phone_number: str | None = None
    ) -> FinancialAnswerSchema:
        """
        Answer a financial question using AI and tools.

        Args:
            question: Natural language question
            consumer_phone_number: Optional phone number identifier

        Returns:
            FinancialAnswerSchema with answer and tool calls

        Raises:
            Exception: If AI fails or tool execution fails
        """
        logger.info(
            f"Financial question: {question} (consumer_phone_number={consumer_phone_number})"
        )

        # Step 1: Get AI to select tools and parameters
        try:
            response = await self.client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                temperature=0.1,  # Low temperature for more consistent tool selection
            )

            ai_response = response.choices[0].message.content
            logger.info(f"AI response: {ai_response}")

            # Parse AI response as JSON
            try:
                parsed_response = json.loads(ai_response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                # Fallback response
                return FinancialAnswerSchema(
                    answer="I'm sorry, I couldn't process your question. Could you rephrase it?",
                    tool_calls=[],
                    confidence="low",
                )

            # Step 2: Execute tool calls
            tool_calls = []
            for tool_call_spec in parsed_response.get("tool_calls", []):
                tool_name = tool_call_spec.get("tool")
                params = tool_call_spec.get("params", {})

                # Add consumer_phone_number to params if provided
                if consumer_phone_number:
                    params["consumer_phone_number"] = consumer_phone_number

                logger.info(f"Executing tool: {tool_name} with params: {params}")

                try:
                    result = await self._execute_tool(tool_name, params)
                    tool_calls.append(
                        ToolCall(tool=tool_name, params=params, result=result)
                    )
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}", exc_info=True)
                    tool_calls.append(
                        ToolCall(
                            tool=tool_name,
                            params=params,
                            result={"error": str(e)},
                        )
                    )

            # Step 3: Return response
            return FinancialAnswerSchema(
                answer=parsed_response.get("answer", "I couldn't generate an answer."),
                tool_calls=tool_calls,
                confidence=parsed_response.get("confidence", "medium"),
            )

        except Exception as e:
            logger.error(f"Financial agent failed: {e}", exc_info=True)
            return FinancialAnswerSchema(
                answer=f"I encountered an error: {str(e)}",
                tool_calls=[],
                confidence="low",
            )

    async def format_response_naturally(self, response: FinancialAnswerSchema) -> str:
        """
        Use AI to convert a FinancialAnswerSchema into natural, conversational English.

        This method takes the structured response (with tool calls and results)
        and asks the AI to rewrite it as natural, human-friendly text without
        any JSON or technical formatting.

        Args:
            response: The FinancialAnswerSchema object to format

        Returns:
            Natural language text formatted by the AI

        Examples:
            >>> response = await agent.ask("How much did I spend this month?")
            >>> natural_text = await agent.format_response_naturally(response)
            >>> print(natural_text)

            You spent 45,000 KES this month across 23 transactions. This includes
            payments to various recipients, with your largest expense being...
        """
        # Build a summary of tool calls and results for the AI
        tool_summary = []
        for i, tool_call in enumerate(response.tool_calls, 1):
            tool_info = f"Tool {i}: {tool_call.tool}\n"
            tool_info += f"Parameters: {json.dumps(tool_call.params, indent=2)}\n"
            tool_info += f"Result: {json.dumps(self._serialize_result(tool_call.result), indent=2)}"
            tool_summary.append(tool_info)

        tools_text = (
            "\n\n".join(tool_summary) if tool_summary else "No tools were used."
        )

        # Create a prompt for the AI to format naturally
        formatting_prompt = f"""You are a helpful financial assistant. I have some financial data that needs to be presented to a user in a natural, conversational way.

Here is the structured data:

ORIGINAL ANSWER:
{response.answer}

CONFIDENCE LEVEL:
{response.confidence}

TOOL CALLS AND RESULTS:
{tools_text}

Please rewrite this information as natural, conversational English text. Follow these guidelines:

1. Write in a friendly, professional tone
2. Use complete sentences and paragraphs
3. Include specific numbers and details from the tool results
4. Don't use JSON format or technical jargon
5. Don't mention "tools" or "parameters" - just present the information naturally
6. If there are multiple pieces of information, organize them logically
7. Round large numbers appropriately (e.g., "22.9 million KES" instead of "22,916,692.00 KES")
8. Use bullet points or numbered lists if it makes the information clearer
9. End with a helpful summary or insight if appropriate

Write ONLY the natural language response, nothing else."""

        try:
            # Call AI to format naturally
            ai_response = await self.client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial assistant that presents financial data in clear, natural language.",
                    },
                    {"role": "user", "content": formatting_prompt},
                ],
                temperature=0.7,  # Higher temperature for more natural language
            )

            natural_text = ai_response.choices[0].message.content.strip()
            logger.info("Successfully formatted response naturally using AI")
            return natural_text

        except Exception as e:
            logger.error(f"Failed to format response naturally: {e}", exc_info=True)
            # Fallback to the original answer if AI formatting fails
            return f"{response.answer}\n\n(Note: Enhanced formatting unavailable)"

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> Any:
        """
        Execute a tool by name with given parameters.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters to pass to the tool

        Returns:
            Tool result

        Raises:
            ValueError: If tool name is unknown
        """
        tool_map = {
            "get_spending_summary": self.financial_tools.get_spending_summary,
            "get_payments_by_recipient": self.financial_tools.get_payments_by_recipient,
            "get_top_recipients": self.financial_tools.get_top_recipients,
            "get_spending_by_category": self.financial_tools.get_spending_by_category,
            "get_payment_trends": self.financial_tools.get_payment_trends,
        }

        tool = tool_map.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Execute the tool
        result = await tool(**params)

        # Convert Decimal to float for JSON serialization
        return self._serialize_result(result)

    def _serialize_result(self, result: Any) -> Any:
        """
        Convert result to JSON-serializable format.

        Args:
            result: Tool result

        Returns:
            JSON-serializable result
        """
        from datetime import datetime
        from decimal import Decimal

        if isinstance(result, dict):
            return {k: self._serialize_result(v) for k, v in result.items()}
        elif isinstance(result, list):
            return [self._serialize_result(item) for item in result]
        elif isinstance(result, Decimal):
            return float(result)
        elif isinstance(result, datetime):
            return result.isoformat()
        else:
            return result
