from datetime import datetime


class EventService:
    @staticmethod
    def create_event(
        agent,
        event,
        status,
        event_type,
        severity,
        message,
        duration_ms=None
    ):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "event": event,
            "event_type": event_type,
            "severity": severity,
            "status": status,
            "message": message,
            "duration_ms": duration_ms
        }