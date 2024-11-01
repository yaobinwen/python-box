#!/bin/sh

usage() {
  cat <<__EOS__
usage: $0 <PY-MINOR-VERSION> <PY-FILE> [PY-ARGS]

  PY-MINOR-VERSION: The minor version of the Python, such as 13.
  PY-FILE: The Python file to be run.
  PY-ARGS: The Python CLI arguments that are passed to the Python interpreter.
__EOS__
}

test $# -ge 2 || {
  usage
  exit 1
}

PY_MINOR_VER="$1"
PY_FILE="$2"
shift 2

PY_VER=
if [ -z "$PY_MINOR_VER" ]; then
  PY_VER="latest"
else
  PY_VER="3.$PY_MINOR_VER"
fi

echo "PY_VER=$PY_VER"
echo "$@"

docker run \
  -it --rm \
  --name my-running-script \
  -v "$PWD":/usr/src/myapp \
  -w /usr/src/myapp \
  "python:$PY_VER" \
  python "$@" "$PY_FILE"
