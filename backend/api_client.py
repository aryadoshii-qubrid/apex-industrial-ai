import requests
import json
import re
import time
from config.settings import settings
from backend.schemas import ChatResponse, UsageMetrics
from backend.utils import encode_image_to_base64

def chat_with_industrial_ai(
    current_question: str, 
    image_file, 
    chat_history: list, 
    system_prompt: str
) -> ChatResponse:
    
    start_time = time.time()  # <--- Start Timer

    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Build Messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 2. Add Current Input
    user_content = [{"type": "text", "text": current_question}]
    if image_file:
        base64_img = encode_image_to_base64(image_file)
        user_content.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.6,
        "stream": False
    }

    try:
        response = requests.post(settings.API_URL, headers=headers, json=payload)
        
        # <--- Stop Timer & Calculate ---
        end_time = time.time()
        latency = round(end_time - start_time, 2)
        # -------------------------------

        if response.status_code != 200:
            raise RuntimeError(f"API Error: {response.text}")

        data = response.json()
        
        # Parse Content
        if 'choices' in data:
            content = data['choices'][0]['message']['content']
        elif 'content' in data:
            content = data['content']
        else:
            content = "Error: No content returned."

        # Parse Usage
        raw_usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
        total_tokens = raw_usage.get('total_tokens', 0)
        
        # Calculate Speed (Tokens per Second)
        # Avoid division by zero
        tps = round(total_tokens / latency, 2) if latency > 0 else 0

        # Create Enhanced Metrics Object
        metrics = UsageMetrics(
            prompt_tokens=raw_usage.get('prompt_tokens', 0),
            completion_tokens=raw_usage.get('completion_tokens', 0),
            total_tokens=total_tokens,
            latency=latency,
            throughput=tps
        )

        return ChatResponse(content=content, usage=metrics)

    except Exception as e:
        raise RuntimeError(f"Connection failed: {str(e)}")