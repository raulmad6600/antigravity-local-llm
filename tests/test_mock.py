#!/usr/bin/env python3
"""
Script to test the API without Ollama (using mock responses)
Useful for verifying that the architecture works correctly
"""
import asyncio
from core.models import Task, AgentContext
from core.agents.planner import PlannerAgent
from core.agents.coder import CoderAgent
from core.agents.reviewer import ReviewerAgent
from core.orchestrator.engine import Orchestrator


# Mock LLM that simulates responses without connecting to Ollama
class MockLLM:
    def __init__(self, model: str = "mock"):
        self.model = model
    
    async def generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        # Identify which agent is calling based on prompt content
        if "technical planner" in prompt_lower:
            response = "PLAN:\n1. Analyze requirements\n2. Design solution\n3. Implement\n4. Test"
            print(f"   [MockLLM] → PLANNER response")
            return response
        elif "software engineer" in prompt_lower:
            response = """def hello_world():
    '''Simple hello world function'''
    print('Hello, World!')
    return True
"""
            print(f"   [MockLLM] → CODER response")
            return response
        elif "code reviewer" in prompt_lower:
            response = "PASS - Code is well-structured, includes documentation, and follows Python best practices."
            print(f"   [MockLLM] → REVIEWER response (PASS)")
            return response
        else:
            print(f"   [MockLLM] → UNKNOWN (prompt: {prompt_lower[:40]}...)")
            return "UNKNOWN RESPONSE"


async def test_orchestrator():
    """Test the orchestrator with mock LLM"""
    print("\n" + "="*60)
    print("🧪 ORCHESTRATOR TEST (Without Ollama)")
    print("="*60)
    
    # Create orchestrator with mock LLM
    mock_llm = MockLLM()
    orchestrator = Orchestrator(mock_llm)
    
    # Create test task
    test_task = Task(
        prompt="Write a simple Python function that returns 'Hello, World!'"
    )
    
    print(f"\n📋 Task: {test_task.prompt}\n")
    
    # Ejecutar orquestador
    try:
        result = await orchestrator.run(test_task, max_iterations=1)
        
        print(f"\n📊 Resultado completo: {result}\n")
        
        print("📊 RESULTS:")
        print("\n1️⃣ PLAN:")
        print("-" * 40)
        plan = result.get("plan", "N/A")
        if plan and plan != "N/A":
            print(plan[:100] + ("..." if len(plan) > 100 else ""))
        else:
            print(plan)
        
        print("\n2️⃣ IMPLEMENTATION:")
        print("-" * 40)
        impl = result.get("implementation", "N/A")
        if impl and impl != "N/A":
            print(impl[:100] + ("..." if len(impl) > 100 else ""))
        else:
            print(impl)
        
        print("\n3️⃣ REVIEW:")
        print("-" * 40)
        review = result.get("review", "N/A")
        if review and review != "N/A":
            print(review[:100] + ("..." if len(review) > 100 else ""))
        else:
            print(review)
        
        print("\n" + "="*60)
        if "error" not in result:
            print("✅ Test completed successfully!")
        else:
            print("⚠️  Test completed with max iterations reached")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
