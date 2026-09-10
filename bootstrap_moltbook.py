import requests

URL = "https://www.moltbook.com/skill.md"


def main():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    print(response.text)


if __name__ == "__main__":
    main()
