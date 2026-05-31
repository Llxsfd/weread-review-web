import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import httpx

from app.api.deps import get_current_user
from app.db.models import User, Setting, Highlight, HighlightAiChat, Book
from app.db.session import get_db
from app.core.crypto import decrypt_api_key

router = APIRouter(prefix="/api/highlights", tags=["ai-chat"])


@router.post("/{highlight_id}/ai-chat/stream")
async def stream_ai_chat(
    highlight_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_message = payload.get("message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    setting = db.query(Setting).filter(Setting.user_id == current_user.id, Setting.key == "ai_api_key").first()
    if not setting or not setting.value:
        raise HTTPException(status_code=400, detail="AI API Key not configured")

    try:
        api_key = decrypt_api_key(setting.value)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt AI API Key")

    highlight = db.query(Highlight).filter(Highlight.id == highlight_id, Highlight.user_id == current_user.id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    book = db.query(Book).filter(Book.book_id == highlight.book_id, Book.user_id == current_user.id).first()
    book_title = book.title if book else "Unknown"

    system_prompt = (
        "你是一个专注于阅读理解的读书助手。以下是用户当前正在复习的划线段落："
        f"【{highlight.mark_text}】，出自《{book_title}》。\n"
        "你的主要任务是解答用户关于这段划线的疑问。如果用户的问题看似偏离了划线内容，"
        "请尝试将他的问题与划线概念建立联系并给予启发；若完全无法联系，请委婉拒绝并引导用户回到划线探讨。"
    )

    history_records = (
        db.query(HighlightAiChat)
        .filter(HighlightAiChat.user_id == current_user.id, HighlightAiChat.highlight_id == highlight_id)
        .order_by(HighlightAiChat.id.desc())
        .limit(10)
        .all()
    )
    history_records.reverse()

    messages = [{"role": "system", "content": system_prompt}]
    for record in history_records:
        messages.append({"role": record.role, "content": record.content})

    messages.append({"role": "user", "content": user_message})

    async def event_generator():
        client = httpx.AsyncClient()
        assistant_content = ""
        try:
            async with client.stream(
                "POST",
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-v4-flash",
                    "messages": messages,
                    "stream": True,
                },
                timeout=30.0,
            ) as response:
                if response.status_code != 200:
                    yield f"API request failed with status {response.status_code}".encode("utf-8")
                    return
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            chunk = data_json["choices"][0]["delta"].get("content", "")
                            if chunk:
                                assistant_content += chunk
                                yield chunk.encode("utf-8")
                        except Exception:
                            continue
        finally:
            await client.aclose()
            
            # Save messages to db after stream completes
            # Note: since this is in an async generator running after the endpoint returns, 
            # we need a fresh db session or at least be careful. In FastAPI, the dependency injected db session 
            # might be closed. Let's yield everything first, then we can save.
            # Actually, to avoid session closed errors, it's safer to just instantiate a new session manually.
            from app.db.session import SessionLocal
            with SessionLocal() as local_db:
                user_msg_db = HighlightAiChat(
                    user_id=current_user.id,
                    highlight_id=highlight_id,
                    role="user",
                    content=user_message,
                )
                assistant_msg_db = HighlightAiChat(
                    user_id=current_user.id,
                    highlight_id=highlight_id,
                    role="assistant",
                    content=assistant_content,
                )
                local_db.add(user_msg_db)
                local_db.add(assistant_msg_db)
                local_db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
