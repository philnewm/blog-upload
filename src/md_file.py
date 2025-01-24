import yaml


with open("ansible_molecule_using_vagrant_and_virtualbox.md") as f:
    text: str = f.read()


# TODO create dataclass around markdown file splitting
def get_md_tags(text: str) -> list[str]:
    if text.startswith("---"):
        parts: list[str] = text.split("---", 2)
        return yaml.safe_load(parts[1])
    
    return []


def get_md_title(text: str) -> str:
    if text.startswith("---"):
        parts: list[str] = text.split("---", 2)
        text = parts[2]
    
    if text.startswith("\n# "):
        parts: list[str] = text.split("\n", 2)
        return parts[1].strip("# ")

    return ""


def get_md_content(text: str) -> str:
    if text.startswith("---"):
        parts: list[str] = text.split("---", 2)
        text = parts[2]
    
    if text.startswith("\n# "):
        parts: list[str] = text.split("\n", 2)
        return parts[2].strip()

    return text


print(get_md_content(text))
