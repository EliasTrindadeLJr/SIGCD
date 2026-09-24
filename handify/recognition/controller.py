import time


class GestureController:

    def __init__(self, config, executor):
        self.config = config
        self.executor = executor
        self.active_gesture = None
        self.last_execution = {}

    def process(self, gesture_id, confidence):

        # Nenhum gesto reconhecido.
        if not gesture_id:
            self.active_gesture = None
            return False

        gesture = self.config.get(gesture_id)

        if not gesture:
            self.active_gesture = gesture_id
            return False

        if not gesture.get("enabled", True):
            self.active_gesture = gesture_id
            return False

        minimum_confidence = float(
            gesture.get(
                "min_confidence",
                0.65
            )
        )

        if confidence < minimum_confidence:
            return False

        now = time.monotonic()

        cooldown = max(
            0.0,
            float(
                gesture.get(
                    "cooldown",
                    0.5
                )
            )
        )

        previous = self.last_execution.get(
            gesture_id,
            0.0
        )

        # Impede a execução até o cooldown terminar.
        if now - previous < cooldown:
            self.active_gesture = gesture_id
            return False

        self.executor.execute(
            gesture.get("action")
        )

        self.last_execution[gesture_id] = now
        self.active_gesture = gesture_id

        return True