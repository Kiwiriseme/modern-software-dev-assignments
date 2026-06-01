import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[str] = []
    for line in lines:
        normalized = line.lower()
        matched = False

        if normalized.startswith("todo:") or normalized.startswith("action:"):
            results.append(line)
            matched = True

        if line.endswith("!"):
            if not matched:
                results.append(line)
                matched = True

        if normalized.startswith("[ ] "):
            task = line[4:]
            if not matched:
                results.append(task)
                matched = True

        if not matched and re.search(r"\b(by|due)\s+\S+", normalized):
            results.append(line)
            matched = True

        if not matched and (
            normalized.startswith("[high]")
            or normalized.startswith("[medium]")
            or normalized.startswith("[low]")
        ):
            results.append(line)

    return results
