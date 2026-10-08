import base64
import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.live_workout import LiveWorkoutAnalyzer

router = APIRouter(prefix="/live", tags=["Live Workout"])

SUPPORTED_EXERCISES = {"squat", "pushup", "pullup"}


@router.websocket("/workout")
async def live_workout(websocket: WebSocket):
    await websocket.accept()
    analyzer = None

    try:
        init_message = await websocket.receive_json()
        exercise = str(init_message.get("exercise", "squat")).lower()

        if exercise not in SUPPORTED_EXERCISES:
            await websocket.send_json({
                "type": "error",
                "message": f"Unsupported exercise. Choose one of: {', '.join(sorted(SUPPORTED_EXERCISES))}",
            })
            await websocket.close(code=1008)
            return

        analyzer = LiveWorkoutAnalyzer(exercise)
        await websocket.send_json({
            "type": "ready",
            "exercise": exercise,
            "message": "Live workout started",
        })

        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "frame":
                encoded = message.get("data", "")
                if "," in encoded:
                    encoded = encoded.split(",", 1)[1]
                frame = base64.b64decode(encoded)
                result = analyzer.process_jpeg(frame)
                result["type"] = "analysis"
                await websocket.send_json(result)

            elif message_type == "stop":
                await websocket.send_json({
                    "type": "summary",
                    "summary": analyzer.session.summary(),
                })
                break

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        if analyzer:
            analyzer.close()
