from __future__ import annotations

import argparse
from pathlib import Path


PROXY_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "HTTP_PROXY": ("HTTP_PROXY", "http_proxy"),
    "HTTPS_PROXY": ("HTTPS_PROXY", "https_proxy"),
    "ALL_PROXY": ("ALL_PROXY", "all_proxy"),
    "NO_PROXY": ("NO_PROXY", "no_proxy"),
}


def parse_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        if not key:
            continue

        values[key] = value.strip()

    return values


def render_template(template_path: Path, env_values: dict[str, str]) -> str:
    output_lines: list[str] = []
    inside_env_block = False

    for raw_line in template_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()

        if stripped == "```env":
            inside_env_block = True
            continue
        if stripped == "```" and inside_env_block:
            inside_env_block = False
            continue
        if not inside_env_block:
            continue

        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            output_lines.append(raw_line)
            continue

        key, default_value = raw_line.split("=", 1)
        value = default_value
        for alias in PROXY_KEY_ALIASES.get(key, (key,)):
            if alias in env_values:
                value = env_values[alias]
                break
        output_lines.append(f"{key}={value}")

    return "\n".join(output_lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Generate my-hermes-bootstrap.env from ~/.hermes/.env using the documented template keys."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("~/.hermes/.env").expanduser(),
        help="Source env file, default: ~/.hermes/.env",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=repo_root / "reference" / "env-template.md",
        help="Template file, default: reference/env-template.md",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "my-hermes-bootstrap.env",
        help="Output env file, default: my-hermes-bootstrap.env",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source_path = args.source.expanduser().resolve()
    template_path = args.template.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    if not source_path.is_file():
        parser.error(f"source env file not found: {source_path}")
    if not template_path.is_file():
        parser.error(f"template file not found: {template_path}")

    env_values = parse_env_file(source_path)
    rendered = render_template(template_path, env_values)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"Generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())