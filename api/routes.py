from fastapi import APIRouter, Depends, HTTPException
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
import logging

logger = logging.getLogger(__name__)

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


@router.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    return {
        "object": "list",
        "data": [
            {
                "id": "local",
                "object": "model",
                "owned_by": "antigravity",
                "permission": []
            }
        ]
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
    try:
        task = Task(prompt=request.prompt, metadata=request.metadata)
        result = await orchestrator.run(task, max_iterations=settings.max_iterations)
        
        return QueryResponse(
            result=result,
            status="success"
        )
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


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
    try:
        # Extract the user prompt from the messages
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise ValueError("No user message found in request")
        
        logger.info(f"Processing chat completion request: {user_message[:100]}...")
        
        # Run the orchestrator pipeline
        task = Task(prompt=user_message)
        result = await orchestrator.run(task, max_iterations=settings.max_iterations)
        
        # Extract response content - handle both success and error cases
        if "error" in result:
            response_content = f"Error: {result.get('error', 'Unknown error occurred')}"
        else:
            response_content = result.get("implementation", result.get("review", "No response generated"))
        
        choice = Choice(
            index=0,
            message=MessageModel(role="assistant", content=response_content),
            finish_reason="stop"
        )
        
        response = ChatCompletionResponse(
            model=request.model,
            choices=[choice]
        )
        
        logger.info(f"Chat completion successful, response length: {len(response_content)}")
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {type(e).__name__}: {str(e)}", exc_info=True)
        
        # Return error in OpenAI-compatible format
        choice = Choice(
            index=0,
            message=MessageModel(
                role="assistant",
                content=f"I encountered an error processing your request: {str(e)[:200]}"
            ),
            finish_reason="error"
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
    try:
        result = await orchestrator.run(
            task,
            max_iterations=settings.max_iterations
        )
        return result
    except Exception as e:
        logger.error(f"Task execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task error: {str(e)}")
