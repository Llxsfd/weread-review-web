import edge_tts
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/stream")
async def stream_tts(text: str = Query(..., description="Text to synthesize")):
    """
    Stream synthesized audio from text using edge-tts.
    """
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    
    async def audio_stream():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")
