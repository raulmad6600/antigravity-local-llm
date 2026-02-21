from core.agents.base import BaseAgent
from core.models import AgentContext, AgentResult


class ReviewerAgent(BaseAgent):
    name = "Reviewer"

    async def run(self, context: AgentContext) -> AgentResult:
        prompt = f"""
You are a strict code reviewer.

Review the following implementation:
{context.intermediate.get("implementation")}

Respond with:
PASS or FAIL
Then explain.
"""
        output = await self.llm.generate(prompt)

        status = "PASS" if "PASS" in output.upper() else "FAIL"

        return AgentResult(
            output=output,
            status=status
        )