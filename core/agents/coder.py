from core.agents.base import BaseAgent
from core.models import AgentContext, AgentResult


class CoderAgent(BaseAgent):
    name = "Coder"

    async def run(self, context: AgentContext) -> AgentResult:
        prompt = f"""
You are a senior software engineer.

Based on this plan:
{context.intermediate.get("plan")}

Generate implementation details.
"""
        output = await self.llm.generate(prompt)

        return AgentResult(
            output=output,
            status="CONTINUE"
        )