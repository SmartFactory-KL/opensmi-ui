import re
import subprocess
import tempfile
from pathlib import Path

from app_config.app_config import AppConfig
from app_config.write import write_config_documentation

TIMESTAMP_PATTERN = re.compile(
    r"^(?:# )?Created at: .*$",
    re.MULTILINE,
)


def normalize(content: str) -> str:
    return TIMESTAMP_PATTERN.sub("Created at: <generated>", content)


def main() -> None:
    tracked_files = [
        Path("docs/config/config.example.yml"),
        Path("docs/config/DefaultConfiguration.md"),
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        write_config_documentation(
            AppConfig(),
            env_prefix="OPENSMI_UI",
            output_dir=temp_path,
        )

        for tracked_file in tracked_files:
            generated_file = temp_path / tracked_file.name

            if not tracked_file.is_file():
                raise SystemExit(
                    f"Missing configuration documentation: {tracked_file}"
                )

            if not generated_file.is_file():
                raise SystemExit(
                    f"Generator did not create: {generated_file}"
                )

            expected = normalize(tracked_file.read_text(encoding="utf-8"))
            actual = normalize(generated_file.read_text(encoding="utf-8"))

            if expected != actual:
                print(f"Configuration documentation is outdated: {tracked_file}")
                print()
                print("Run:")
                print("  uv run python3 -m script.update_config_docs")
                print()
                print("to regenerate the documentation.")

                diff = subprocess.run(
                    [
                        "diff",
                        "-u",
                        str(tracked_file),
                        str(generated_file),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                print(diff.stdout)
                raise SystemExit(1)

    print("Configuration documentation is up to date.")


if __name__ == "__main__":
    main()
