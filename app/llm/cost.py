import os
from datetime import datetime, timezone


INPUT_COST_PER_1M = float(
    os.getenv("LLM_INPUT_COST_PER_1M", "0.0")
)

OUTPUT_COST_PER_1M = float(
    os.getenv("LLM_OUTPUT_COST_PER_1M", "0.0")
)


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_COST_PER_1M

    output_cost = (
        completion_tokens / 1_000_000
    ) * OUTPUT_COST_PER_1M

    return input_cost + output_cost


def log_llm_usage(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int
):
    cost = calculate_cost(
        prompt_tokens,
        completion_tokens
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    log_line = (
        f"{timestamp} | "
        f"model={model} | "
        f"prompt_tokens={prompt_tokens} | "
        f"completion_tokens={completion_tokens} | "
        f"total_tokens={total_tokens} | "
        f"estimated_cost_usd={cost:.8f}"
    )

    print(f"LLM COST LOG: {log_line}")

    with open("llm_cost.log", "a") as file:
        file.write(log_line + "\n")