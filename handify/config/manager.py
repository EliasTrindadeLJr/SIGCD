import json
from pathlib import Path


class ConfigManager:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).with_name("gestures.json")

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.save({"gestures": {}})

        self.data = self.load()

    def load(self):
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("O arquivo de configuração precisa ser um objeto JSON.")

            data.setdefault("gestures", {})

            return data

        except (json.JSONDecodeError, OSError, ValueError):
            return {
                "gestures": {}
            }

    def save(self, data=None):
        if data is not None:
            self.data = data

        temporary = self.path.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

        temporary.replace(self.path)

    def all_gestures(self):
        return self.data.setdefault("gestures", {})

    def get(self, gesture_id):
        return self.all_gestures().get(gesture_id)

    def set(self, gesture_id, gesture):
        self.all_gestures()[gesture_id] = gesture
        self.save()

    def remove(self, gesture_id):
        self.all_gestures().pop(gesture_id, None)
        self.save()