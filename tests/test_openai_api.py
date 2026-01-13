import httpx
import json
import asyncio

async def test_chat():
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "advence-rag-agent",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! What can you do?"}
        ],
        "stream": False
    }
    
    print("Testing non-streaming...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error testing non-streaming: {e}")

async def test_streaming():
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "advence-rag-agent",
        "messages": [
            {"role": "user", "content": "Tell me a short joke."}
        ],
        "stream": True
    }
    
    print("\nTesting streaming...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Status Code: {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        content = line[6:]
                        if content == "[DONE]":
                            print("\n[DONE]")
                            break
                        try:
                            data = json.loads(content)
                            delta = data["choices"][0].get("delta", {})
                            text = delta.get("content", "")
                            print(text, end="", flush=True)
                        except json.JSONDecodeError:
                            print(f"\nJson Error on line: {line}")
    except Exception as e:
        print(f"Error testing streaming: {e}")

if __name__ == "__main__":
    # Note: These tests require the server to be running.
    # To run the server: python src/advence_rag/main.py
    asyncio.run(test_chat())
    asyncio.run(test_streaming())
