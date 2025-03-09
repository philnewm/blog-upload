import pytest
import yaml
import random
import uuid
from pathlib import Path
from mdgen import MarkdownOutputGenerator


def _generated_markdown(tmp_path: Path) -> str:
    """Reads from a YAML file and creates a randomized Markdown article."""
    
    with open("tests/integrationtests/articles.yml", "r") as file:
        md_content: list[dict[str, str]] = yaml.safe_load(file)
    
    unique_id: str = str(uuid.uuid4().int)[:6]
    target_path: Path = tmp_path / f"{unique_id}.md"
    md = MarkdownOutputGenerator(filepath=str(target_path))

    md.add_header(
        text=f"{random.choice(md_content['titles'])} - {unique_id}",
        header_level=1,
        linebreak=True,
    )

    for _ in range(random.randint(2, 4)):
        md.add_linebreak()
        md.add_header(
            text=random.choice(md_content["headers"]), header_level=2,
            linebreak=True,
            )
        md.add_linebreak()
        md.add_paragraph(random.choice(md_content["paragraphs"]))

    code_block = random.choice(md_content["code_blocks"])
    md.add_linebreak()
    md.add_code_block(
        code=code_block["content"],
        language=code_block["language"],
        )

    md.add_linebreak()
    md.add_blockquote(random.choice(md_content["quotes"]))

    list_block = random.choice(md_content["lists"])
    if list_block["type"] == "ordered":
        md.add_linebreak()
        md.add_ordered_list(
            list_items_list=list_block["items"],
            linebreak=True,
            )
    else:
        md.add_linebreak()
        md.add_unordered_list(
            list_items_list=list_block["items"],
            linebreak=True,
            )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    md.create_file_from_output(filepath=str(target_path))
    return str(target_path)


@pytest.fixture(scope="function")
def generated_markdown(tmp_path: Path) -> str:
    """Retruns a randomized Markdown article."""

    return _generated_markdown(tmp_path)

@pytest.fixture
def generated_markdown_list(tmp_path: Path) -> list[str]:
    """Generates multiple unique Markdown files by calling `_generated_markdown` multiple times."""

    return [_generated_markdown(tmp_path=tmp_path) for _ in range(5)]
