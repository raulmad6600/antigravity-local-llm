from fastapi import APIRouter, Depends
from core.models import Task
from .deps import get_orchestrator
from .config import settings
from .schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    MessageModel,
    QueryRequest,
    QueryResponse,
)

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "app": settings.app_name,
        "debug": settings.debug
    }


@router.post("/v1/query")
async def query(request: QueryRequest, orchestrator=Depends(get_orchestrator)):
    """
    Execute a multi-agent pipeline for code generation and review.
    
    This endpoint runs the full pipeline:
    1. Planner: Creates execution plan
    2. Coder: Implements solution
    3. Reviewer: Validates implementation
    """
    task = Task(prompt=request.prompt, metadata=request.metadata)
    result = await orchestrator.run(task, max_iterations=settings.max_iterations)
    
    return QueryResponse(
        result=result,
        status="success"
    )


@router.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    orchestrator=Depends(get_orchestrator)
):
    """
    OpenAI-compatible chat completion endpoint.
    
    This endpoint accepts OpenAI-style chat requests and returns
    OpenAI-compatible responses. Compatible with VS Code Continue extension.
    """
    # Extract the user prompt from the messages
    user_message = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break
    
    if not user_message:
        raise ValueError("No user message found in request")
    
    # Run the orchestrator pipeline
    task = Task(prompt=user_message)
    result = await orchestrator.run(task, max_iterations=settings.max_iterations)
    
    # Format response according to OpenAI spec
    response_content = result.get("implementation", result.get("review", ""))
    
    choice = Choice(
        index=0,
        message=MessageModel(role="assistant", content=response_content),
        finish_reason="stop"
    )
    
    return ChatCompletionResponse(
        model=request.model,
        choices=[choice]
    )


@router.post("/run")
async def run_task(task: Task, orchestrator=Depends(get_orchestrator)):
    """
    Legacy endpoint for running orchestrator tasks.
    Use /v1/query for new code.
    """
    result = await orchestrator.run(
        task,
        max_iterations=settings.max_iterations
    )
    return result
