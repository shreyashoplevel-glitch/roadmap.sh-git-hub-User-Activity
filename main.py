import sys
import json
import os
import urllib.request
import urllib.error

def load_token():
    try:
        with open(".env") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN"):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass
    return os.environ.get("GITHUB_TOKEN", "")

def fetch_events(username):
    token = load_token()
    url = f"https://api.github.com/users/{username}/events"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found.")
        elif e.code == 403:
            print("Error: API rate limit exceeded. Add a token in .env")
        else:
            print(f"Error: HTTP {e.code}")
        sys.exit(1)
    except urllib.error.URLError:
        print("Error: Network failure. Check your internet connection.")
        sys.exit(1)

def format_event(event):
    etype = event["type"]
    repo = event["repo"]["name"]
    payload = event.get("payload", {})

    if etype == "PushEvent":
        count = len(payload.get("commits", []))
        return f"Pushed {count} commit{'s' if count != 1 else ''} to {repo}"

    elif etype == "IssuesEvent":
        action = payload.get("action", "")
        if action == "opened":
            return f"Opened a new issue in {repo}"
        elif action == "closed":
            return f"Closed an issue in {repo}"
        else:
            return f"{action.capitalize()} an issue in {repo}"

    elif etype == "IssueCommentEvent":
        return f"Commented on an issue in {repo}"

    elif etype == "WatchEvent":
        return f"Starred {repo}"

    elif etype == "ForkEvent":
        return f"Forked {repo}"

    elif etype == "CreateEvent":
        ref_type = payload.get("ref_type", "")
        return f"Created a {ref_type} in {repo}"

    elif etype == "DeleteEvent":
        ref_type = payload.get("ref_type", "")
        return f"Deleted a {ref_type} in {repo}"

    elif etype == "PullRequestEvent":
        action = payload.get("action", "")
        return f"{action.capitalize()} a pull request in {repo}"

    elif etype == "PullRequestReviewEvent":
        return f"Reviewed a pull request in {repo}"

    elif etype == "PullRequestReviewCommentEvent":
        return f"Commented on a pull request in {repo}"

    elif etype == "ReleaseEvent":
        return f"Published a release in {repo}"

    elif etype == "MemberEvent":
        action = payload.get("action", "")
        return f"{action.capitalize()} a member in {repo}"

    elif etype == "PublicEvent":
        return f"Made {repo} public"

    else:
        return f"{etype} in {repo}"

def main():
    if len(sys.argv) < 2:
        print("Usage: github-activity <username>")
        sys.exit(1)

    username = sys.argv[1]
    events = fetch_events(username)

    if not events:
        print(f"No recent activity found for '{username}'.")
        sys.exit(0)

    print(f"\nRecent activity for {username}:\n")
    for event in events:
        print(f"  - {format_event(event)}")
    print()

main()
