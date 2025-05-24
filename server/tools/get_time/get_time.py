from datetime import date


class GetTime:
    description = "Get the current date in YYYY-MM-DD format. Use whenever you need to know today's date."

    properties = {
        "date": {
            "type": "string",
            "description": "Current date in YYYY-MM-DD format"
        }
    }
    
    def get_todays_date():
        return date.today().isoformat()
    