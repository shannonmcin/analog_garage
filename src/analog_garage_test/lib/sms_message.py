from dataclasses import dataclass


@dataclass(frozen=True)
class SmsMessage:
    text: str
    dst: str
