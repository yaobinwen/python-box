#!/bin/sh

usage() {
  cat <<__EOS__
usage: $0 <PY-FILE> [PY-ARGS]

  PY-FILE: The Python file to be run.
  PY-ARGS: The Python CLI arguments that are passed to the Python interpreter.
__EOS__
}

test $# -ge 1 || {
  usage
  exit 1
}

PY_FILE="$1"
shift 1

PY_VER="latest"
echo "PY_VER=$PY_VER"
echo "$@"

docker run \
  -it --rm \
  --name my-running-script \
  -v "$PWD":/usr/src/myapp \
  -w /usr/src/myapp \
  "python:$PY_VER" \
  python "$@" "$PY_FILE"
