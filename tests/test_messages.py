import json

from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.stats_message import StatsMessage

sms_text = "we've been trying to reach you about your car's extended warranty"
sms_dest = "1-800-leave-me-alone"
sms_msg = SmsMessage(sms_text, sms_dest)
sms_json = json.dumps({"text": sms_text, "dest": sms_dest})


stats_res = False
stats_time = 1.67
stats_msg = StatsMessage(stats_res, stats_time)
stats_json = json.dumps({"success": stats_res, "time_waited": stats_time})


def test_sms_message():
    assert sms_msg.to_json_string() == sms_json
    assert SmsMessage.from_json_string(sms_json) == sms_msg
    assert SmsMessage.from_json_string(sms_msg.to_json_string()) == sms_msg


def test_stats_message():
    assert stats_msg.to_json_string() == stats_json
    assert StatsMessage.from_json_string(stats_json) == stats_msg
    assert StatsMessage.from_json_string(stats_msg.to_json_string()) == stats_msg
