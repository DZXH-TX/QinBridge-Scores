"""GitHub score gate: read-only validation and separate exact-commit approval."""
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_scores import SHA, git, require, validate_repository

REPOSITORY = "DZXH-TX/QinBridge-Scores"
CONTEXT = "qinbridge/score-security"


def api(path, method="GET", data=None):
    request = Request("https://api.github.com/repos/" + REPOSITORY + "/" + path,
                      data=None if data is None else json.dumps(data).encode(), method=method,
                      headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
                               "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "QinBridge-score-gate"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def output(**values):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as destination:
        for key, value in values.items():
            value = str(value)
            require("\n" not in value and "\r" not in value, "Invalid job output")
            destination.write(f"{key}={value}\n")


def check(head, base):
    require(SHA.fullmatch(head) and SHA.fullmatch(base), "Expected full commit SHAs")
    # Fetch Git objects only. Candidate .gitattributes, hooks, tools and workflows never run.
    git("fetch", "--no-tags", "--depth=1", "origin", base, head)
    return validate_repository(head, base, workers=4)


def validate_run():
    run = api("actions/runs/" + str(int(os.environ["SOURCE_RUN_ID"])))
    require(run["event"] == "pull_request" and run["path"] == ".github/workflows/score-check.yml", "Unexpected source workflow")
    head = run["head_sha"]
    require(SHA.fullmatch(head), "Invalid source commit")
    # Fork workflow_run payloads may omit pull_requests. Resolve via GitHub, not an artifact.
    candidates = api(f"commits/{head}/pulls?per_page=100")
    candidates = [p for p in candidates if p["state"] == "open" and p["head"]["sha"] == head
                  and p["base"]["ref"] == "main" and p["base"]["repo"]["full_name"] == REPOSITORY]
    if not candidates:
        print("No current open PR for this run; no approval or merge.")
        return
    require(len(candidates) == 1, "Ambiguous PR association")
    pr = api("pulls/" + str(candidates[0]["number"]))
    base = pr["base"]["sha"]
    require(SHA.fullmatch(base), "Invalid base commit")
    output(number=pr["number"], head=head, base=base, eligible="false")
    require(base == os.environ["GITHUB_SHA"], "Default branch changed; rerun checks with the current policy")
    comparison = api(f"compare/{base}...{head}")
    require(comparison["behind_by"] == 0, "PR must be updated with main before validation")
    result = check(head, base)
    # A modified/failed upstream workflow is never sufficient evidence for approval.
    require(run["conclusion"] == "success", "Source checks did not succeed")
    output(eligible=str(result["data_only"] and not pr["draft"]).lower())
    print(json.dumps(result))


def current_pr(number, head, base):
    pr = api(f"pulls/{number}")
    require(pr["state"] == "open" and not pr["draft"] and pr["base"]["ref"] == "main"
            and pr["head"]["sha"] == head and pr["base"]["sha"] == base,
            "PR changed after validation; a fresh check is required")
    return pr


def publish():
    number = int(os.environ["PR_NUMBER"])
    head, base = os.environ["HEAD_SHA"], os.environ["BASE_SHA"]
    require(SHA.fullmatch(head) and SHA.fullmatch(base), "Invalid validated commit")
    passed = os.environ["VALIDATION_RESULT"] == "success"
    api(f"statuses/{head}", "POST", {"state": "success" if passed else "failure", "context": CONTEXT,
        "description": "Trusted score data validation passed" if passed else "Score data validation failed",
        "target_url": f"https://github.com/{REPOSITORY}/actions/runs/{int(os.environ['GITHUB_RUN_ID'])}"})
    if not passed or os.environ.get("AUTO_ELIGIBLE") != "true":
        print("Status published. This PR is not eligible for automatic approval.")
        return
    current_pr(number, head, base)
    # Do not supersede a human request for changes, even if all data checks pass.
    reviews = []
    for page in range(1, 11):
        batch = api(f"pulls/{number}/reviews?per_page=100&page={page}")
        reviews.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Too many reviews for automatic approval")
    latest = {}
    for review in reviews:
        if review["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[review["user"]["login"]] = review
    if any(review["state"] == "CHANGES_REQUESTED" for review in latest.values()):
        print("A reviewer requested changes; leaving the PR for manual review.")
        return
    existing = latest.get("github-actions[bot]", {})
    if existing.get("state") != "APPROVED" or existing.get("commit_id") != head:
        api(f"pulls/{number}/reviews", "POST", {"event": "APPROVE", "commit_id": head,
            "body": "此提交仅修改曲谱、目录或随谱来源说明，已通过主分支校验器的 JSON、谱面、目录一致性和资源限制检查。来源说明为可选数据；此检查不要求或核验 CC 等版权许可。"})
    # Give GitHub time to recompute required checks after the status/review writes.
    for attempt in range(6):
        current_pr(number, head, base)
        try:
            result = api(f"pulls/{number}/merge", "PUT", {"sha": head, "merge_method": "squash"})
            require(result.get("merged") is True, "GitHub declined the merge")
            print(f"Approved and merged PR #{number} at {head}.")
            return
        except HTTPError as error:
            if error.code not in (405, 409) or attempt == 5:
                raise
            time.sleep(5)


def main():
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY, "Automation only runs in its configured repository")
    mode = sys.argv[1]
    if mode == "check":
        print(json.dumps(check(os.environ["HEAD_SHA"], os.environ["BASE_SHA"])))
    elif mode == "validate-run":
        validate_run()
    elif mode == "publish":
        publish()
    else:
        raise ValueError("Unknown automation operation")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Escape untrusted strings so they cannot emit GitHub workflow commands.
        print("Score gate failed: " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        sys.exit(1)
