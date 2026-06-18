from __future__ import annotations

import argparse
import os
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
HERMES_ENV = HERMES_HOME / ".env"
HERMES_CONFIG = HERMES_HOME / "config.yaml"

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "my-hermes-bootstrap.env.template"
RESOURCE_DIR = REPO_ROOT / "resource"
RESOURCE_ENV = RESOURCE_DIR / ".env"
RESOURCE_CONFIG = RESOURCE_DIR / "config.yaml"


# ── Config key mapping ─────────────────────────────────────────────────

# Mapping from config.yaml dot-path to bootstrap env var name
CONFIG_TO_ENV: dict[str, str] = {
    "memory.write_approval": "MEMORY_WRITE_APPROVAL",
    "skills.write_approval": "SKILLS_WRITE_APPROVAL",
    "display.language": "DISPLAY_LANGUAGE",
}

PROXY_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "HTTP_PROXY": ("HTTP_PROXY", "http_proxy"),
    "HTTPS_PROXY": ("HTTPS_PROXY", "https_proxy"),
    "ALL_PROXY": ("ALL_PROXY", "all_proxy"),
    "NO_PROXY": ("NO_PROXY", "no_proxy"),
}


# ── Core helpers ───────────────────────────────────────────────────────

def resolve_source_env() -> Path:
    """Resolve the .env source: Hermes installation → resource fallback."""
    if HERMES_ENV.is_file():
        print(f"  source .env: {HERMES_ENV}")
        return HERMES_ENV
    print(f"  [!] {HERMES_ENV} not found, fallback to {RESOURCE_ENV}")
    return RESOURCE_ENV


def resolve_source_config() -> Path:
    """Resolve the config.yaml source: Hermes installation → resource fallback."""
    if HERMES_CONFIG.is_file():
        print(f"  source config: {HERMES_CONFIG}")
        return HERMES_CONFIG
    print(f"  [!] {HERMES_CONFIG} not found, fallback to {RESOURCE_CONFIG}")
    return RESOURCE_CONFIG


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


def _nested_get(cfg: dict, dot_path: str) -> str | None:
    """Navigate nested dict by dot-separated path, returns None if not found."""
    parts = dot_path.split(".")
    current: object = cfg
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    if current is None:
        return None
    if isinstance(current, bool):
        return str(current).lower()
    return str(current)


def read_config_keys(config_path: Path) -> dict[str, str]:
    """Read specific keys from a Hermes config.yaml."""
    if not config_path.is_file():
        print(f"  [!] config not found: {config_path}")
        return {}

    import yaml  # type: ignore[import-untyped]

    try:
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
    except Exception as exc:
        print(f"  [!] failed to parse {config_path}: {exc}")
        return {}

    result: dict[str, str] = {}
    for dot_path, env_key in CONFIG_TO_ENV.items():
        value = _nested_get(cfg, dot_path)
        if value is not None:
            result[env_key] = value
            print(f"  config {dot_path} → {env_key}={value}")
    return result


def render_template(template_path: Path, env_values: dict[str, str]) -> str:
    """Render a plain .env template, substituting values from env_values."""
    output_lines: list[str] = []

    for raw_line in template_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()

        # Preserve blank lines and comments verbatim
        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            output_lines.append(raw_line)
            continue

        # Strip inline comments for key/value parsing, but tolerate them in input
        line_for_parsing = raw_line.split("#", 1)[0].rstrip()
        if "=" not in line_for_parsing:
            output_lines.append(raw_line)
            continue

        key, default_value = line_for_parsing.split("=", 1)
        key = key.strip()
        value = default_value.strip()
        for alias in PROXY_KEY_ALIASES.get(key, (key,)):
            if alias in env_values:
                value = env_values[alias]
                break
        output_lines.append(f"{key}={value}")

    return "\n".join(output_lines).rstrip() + "\n"


# ── CLI ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate my-hermes-bootstrap.env from Hermes installation or resource fallback."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Source .env file (auto: Hermes → resource fallback)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Source config.yaml (auto: Hermes → resource fallback)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=TEMPLATE,
        help="Template file, default: my-hermes-bootstrap.env.template",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "my-hermes-bootstrap.env",
        help="Output env file, default: my-hermes-bootstrap.env",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    template_path = args.template.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    if not template_path.is_file():
        parser.error(f"template not found: {template_path}")

    # ── Resolve sources ────────────────────────────────────────────
    print("=== Source resolution ===")

    env_source = args.source.expanduser().resolve() if args.source else resolve_source_env()
    config_source = args.config.expanduser().resolve() if args.config else resolve_source_config()

    if not env_source.is_file():
        parser.error(f"source .env not found: {env_source}")
    if not config_source.is_file():
        parser.error(f"source config not found: {config_source}")

    # ── Gather values ──────────────────────────────────────────────
    env_values = parse_env_file(env_source)

    # Supplement from config.yaml (lower priority — .env values win)
    for k, v in read_config_keys(config_source).items():
        if k not in env_values:
            env_values[k] = v
            print(f"  config supplement: {k}={v}")

    # ── Render ─────────────────────────────────────────────────────
    rendered = render_template(template_path, env_values)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"\nGenerated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
