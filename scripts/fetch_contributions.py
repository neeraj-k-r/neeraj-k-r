import json
import os
import urllib.request
from datetime import datetime, timezone

USERNAME = "neeraj-k-r"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "github_stats.json")


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "neeraj-k-r-profile-cards/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    contrib_data = fetch_json(
        f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
    )
    repos_data = fetch_json(
        f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=100"
    )

    public_repos = [r for r in repos_data if not r.get("fork")]
    total_stars = sum(int(r.get("stargazers_count", 0)) for r in repos_data)

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_last_year": int(contrib_data.get("total", {}).get("lastYear", 0)),
        "contributions": contrib_data.get("contributions", []),
        "public_repo_count": len(repos_data),
        "original_repo_count": len(public_repos),
        "total_stars": total_stars,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(
        f"Saved {len(payload['contributions'])} days, "
        f"total={payload['total_last_year']}, repos={payload['public_repo_count']}"
    )


if __name__ == "__main__":
    main()
