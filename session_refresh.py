import requests

from config import BASE_URL


def session_refresh(session_token: str) -> requests.Response:
    url = BASE_URL + "/api/auth/session"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {"session_token": session_token}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


if __name__ == "__main__":
    session_token = "session_token"
    resp = session_refresh(session_token)
    print(resp.text)
