import json
from dataclasses import dataclass


@dataclass(frozen=True)
class SmsMessage:
    text: str
    dest: str

    def to_json_string(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json_string(cls, js: str) -> "SmsMessage":
        return cls(**json.loads(js))
