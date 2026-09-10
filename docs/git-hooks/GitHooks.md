# Git hooks in use
This project makes use of a simple git hook to: 

 - update `/docs/DefaultConfiguration.md`
 - update `/docs/openapi.yaml`

To ensure that they never get out-of-sync. 

It makes use of python scripts within this folder.

To add, please create a file `/.git/pre-commit` with this content:

~~~bash
#!/bin/bash

# exit immediatly on fail
VENV_DIR=".venv"
SCRIPT_TO_RUN="docs/git-hooks/pre_commit_update.py"

# cd into top level repo folder
REPOSITORY_ROOT=$(git rev-parse --show-toplevel)
cd "$REPOSITORY_ROOT"

if [ -d "$VENV_DIR" ]; then
  echo "Found $VENV_DIR. Try to execute $SCRIPT_TO_RUN."
  VENV_PYTHON="$VENV_DIR/bin/python"

  if [ ! -f "$VENV_PYTHON" ]; then
    echo "Python interpreter not found in $VENV_DIR"
    exit 1
  fi

  if [ ! -f "$SCRIPT_TO_RUN" ]; then
    echo "Script $SCRIPT_TO_RUN not found"
    exit 1
  fi
  
  echo "Running $SCRIPT_TO_RUN ..."
  export PYTHONPATH="$REPOSITORY_ROOT"
  OUTPUT=$("$VENV_PYTHON" "$SCRIPT_TO_RUN")

  OUTPUT_STATE=$?

  echo "Script output:"
  echo "$OUTPUT"

  if [ $OUTPUT_STATE -eq 1 ]; then
    echo "Something went wrong. Hook failed."
    exit 1
  fi

  git add docs/DefaultConfiguration.md
  git add docs/openapi.yaml

else
  echo "No $VENV_DIR found. Please make sure a virtual python environment is present within $VENV_DIR."
  exit 1
fi

~~~

> [!note]
> This pre-commit hook assumes, that a [Virtual Environment]() is present within `.venv` containing all dependencies. It will fail it if is not present.
> That might be created using this command:
> ~~~bash
> python3 -m venv .venv
> ~~~

> [!important]
> Make sure, the file is marked as executable. Example: `sudo chown +x pre-commit`
