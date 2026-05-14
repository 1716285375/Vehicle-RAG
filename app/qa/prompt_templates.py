from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompts"


@lru_cache
def load_template(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return path.read_text(encoding="utf-8")


def render_template(name: str, **values: str) -> str:
    return load_template(name).format(**values)


def build_qa_messages(question: str, context: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": load_template("system.tmpl").strip()},
        {"role": "user", "content": render_template("qa.tmpl", question=question, context=context).strip()},
    ]
