import json
from dataclasses import dataclass


@dataclass(frozen=True)
class StatsMessage:
    success: bool
    time_waited: float

    def to_json_string(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json_string(cls, js: str) -> "StatsMessage":
        return cls(**json.loads(js))
