from core.models import Task, AgentContext
from core.agents.planner import PlannerAgent
from core.agents.coder import CoderAgent
from core.agents.reviewer import ReviewerAgent


class Orchestrator:

    def __init__(self, llm):
        self.planner = PlannerAgent(llm)
        self.coder = CoderAgent(llm)
        self.reviewer = ReviewerAgent(llm)

    async def run(self, task: Task, max_iterations: int = 3):
        context_data = {
            "task": task,
            "intermediate": {},
            "memory": {}
        }
        context = AgentContext(**context_data)

        # Planner
        plan_result = await self.planner.run(context)
        context.intermediate["plan"] = plan_result.output

        for _ in range(max_iterations):

            # Coder
            code_result = await self.coder.run(context)
            context.intermediate["implementation"] = code_result.output

            # Reviewer
            review_result = await self.reviewer.run(context)

            if review_result.status == "PASS":
                return {
                    "plan": context.intermediate["plan"],
                    "implementation": code_result.output,
                    "review": review_result.output
                }

        return {
            "error": "Max iterations reached",
            "last_review": review_result.output
        }