#!/usr/bin/env bash

set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "Expected one artifact destination directory." >&2
  exit 2
fi

publisher_id="${ADMOB_PUBLISHER_ID:-}"
if [[ ! "$publisher_id" =~ ^pub-[0-9]+$ ]]; then
  echo "ADMOB_PUBLISHER_ID is missing or invalid." >&2
  exit 1
fi

artifact_directory="$1"
mkdir -p "$artifact_directory"

for site_path in CNAME kr jp docs; do
  cp -a "$site_path" "$artifact_directory/"
done

printf 'google.com, %s, DIRECT, f08c47fec0942fa0\n' "$publisher_id" > "$artifact_directory/app-ads.txt"
unset publisher_id
