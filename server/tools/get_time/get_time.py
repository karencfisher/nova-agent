from datetime import date, datetime
import json


class GetTime:
    description = "Get the current date, day of the week, and time in the local timezone."

    properties = {
        "date": {
            "type": "string",
            "description": "Current date in YYYY-MM-DD format"
        },
        "day": {
            "type": "string",
            "description": "Day of the week"
        },
        "time": {
            "type": "string",
            "description": "Current time in HH:MM:SS format"
        }
    }

    @staticmethod
    def get_todays_date(**kwargs):
        now = datetime.now()
        current_date = now.date().isoformat()
        day_of_week = now.strftime('%A')
        current_time = now.strftime('%H:%M:%S')
        result = {"date": current_date, "day": day_of_week, "time": current_time}
        return json.dumps(result)
