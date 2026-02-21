from core.agents.base import BaseAgent
from core.models import AgentContext, AgentResult


class PlannerAgent(BaseAgent):
    name = "Planner"

    async def run(self, context: AgentContext) -> AgentResult:
        prompt = f"""
You are a senior technical planner.
Create a structured development plan.

Task:
{context.task.prompt}
"""
        output = await self.llm.generate(prompt)

        return AgentResult(
            output=output,
            status="CONTINUE"
        )