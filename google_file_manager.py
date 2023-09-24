import requests

class GoogleFileManager:
    def __init__(self) -> None:
        self.url = ''

    def appendQRData(self, value, sheet_name, session):
        self.url = "https://docs.google.com/forms/d/e/1FAIpQLSdRfh-LhpqTWb6YvX7SJKmUqLZCwLVGOeinF-AN31vWE4bVGw/formResponse?usp=pp_url&entry.1364846059="
        self.url += value
        self.url += "&entry.627658485="
        self.url += sheet_name
        self.url += "&entry.764437109="
        self.url += session
        self.url += "&submit=Submit"

        try:
            response = requests.get(self.url)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print("Saved on the cloud")
                return "Saved on the cloud"
            else:
                print(f"Failed to open URL. Status code: {response.status_code}")
                return f"Failed to open URL. Status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}"
