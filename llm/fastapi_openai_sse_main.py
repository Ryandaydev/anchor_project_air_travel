import os
from collections.abc import AsyncIterable

from fastapi import FastAPI, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")


app = FastAPI(title="LLM Streaming Demo")
client = AsyncOpenAI()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
SYSTEM_PROMPT = "You are a helpful assistant. Be concise, clear, and accurate."


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt to send to the model")
    model: str = Field(default=DEFAULT_MODEL, description="OpenAI model name")
    system_prompt: str = Field(
        default=SYSTEM_PROMPT,
        description="Optional system prompt to control the assistant",
    )


@app.get("/")
async def root():
    return {"message": "API health check successful"}


@app.post("/responses/stream", response_class=EventSourceResponse)
async def responses_stream(payload: ChatRequest) -> AsyncIterable[ServerSentEvent]:
    try:
        stream = await client.responses.create(
            model=payload.model,
            instructions=payload.system_prompt,
            input=payload.prompt,
            stream=True,
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                yield ServerSentEvent(data=event.delta)

            elif event.type == "response.completed":
                yield ServerSentEvent(event="done", data="[DONE]")

        yield ServerSentEvent(raw_data="[DONE]")

    except Exception as exc:
        yield ServerSentEvent(event="error", data=str(exc))
        yield ServerSentEvent(raw_data="[DONE]")


@app.post("/responses")
async def responses(payload: ChatRequest) -> dict[str, str]:
    try:
        response = await client.responses.create(
            model=payload.model,
            instructions=payload.system_prompt,
            input=payload.prompt,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"text": response.output_text}