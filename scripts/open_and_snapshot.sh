#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <canvas-file> <output.png>" >&2
  exit 64
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
canvas_input="$1"
output_input="$2"

if [[ ! -f "$canvas_input" ]]; then
  echo "Canvas file does not exist: $canvas_input" >&2
  exit 66
fi

canvas_abs="$(cd "$(dirname "$canvas_input")" && pwd -P)/$(basename "$canvas_input")"
if [[ "$output_input" = /* ]]; then
  output_abs="$output_input"
else
  output_abs="$(pwd -P)/$output_input"
fi

bash "$script_dir/preflight.sh" "$canvas_abs"
python3 "$script_dir/validate_canvas.py" "$canvas_abs"

probe="$(dirname "$canvas_abs")"
vault_root=""
while [[ "$probe" != "/" ]]; do
  if [[ -d "$probe/.obsidian" ]]; then
    vault_root="$probe"
    break
  fi
  probe="$(dirname "$probe")"
done

if [[ -z "$vault_root" ]]; then
  echo "Could not find a Vault root for $canvas_abs" >&2
  exit 65
fi

relative_path="${canvas_abs#"$vault_root"/}"
canvas_title="$(basename "$canvas_abs" .canvas)"
vault_name="$(obsidian vaults verbose 2>/dev/null | awk -F '\t' -v path="$vault_root" '$2 == path {print $1; exit}')"
if [[ -z "$vault_name" ]]; then
  echo "Vault is not registered with Obsidian: $vault_root" >&2
  exit 69
fi
mkdir -p "$(dirname "$output_abs")"

obsidian vault="$vault_name" open path="$relative_path"

tab_ready=0
for _ in {1..20}; do
  if obsidian vault="$vault_name" tabs 2>/dev/null | grep -Fq "[canvas] $canvas_title"; then
    tab_ready=1
    break
  fi
  sleep 0.25
done

if [[ "$tab_ready" -ne 1 ]]; then
  echo "Canvas did not appear in an Obsidian tab: $canvas_title" >&2
  exit 69
fi

obsidian vault="$vault_name" dev:screenshot path="$output_abs"
if [[ ! -s "$output_abs" ]]; then
  echo "Screenshot was not created: $output_abs" >&2
  exit 74
fi

echo "Opened: $canvas_abs"
echo "Screenshot: $output_abs"
