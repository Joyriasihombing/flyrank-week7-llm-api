import os

from app.llm.client import get_llm_client


def main():
    client = get_llm_client()

    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly the word: ready",
            }
        ],
        temperature=0,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()