#!/usr/bin/env bash
set -u

canvas_path="${1:-}"
ok=1

echo "Checking prerequisites for beautiful-obsidian-canvas..."

if command -v python3 >/dev/null 2>&1; then
  python_version="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
    echo "  OK Python ${python_version}"
  else
    echo "  ERROR Python 3.9 or newer is required (found ${python_version})"
    ok=0
  fi
else
  echo "  ERROR python3 is not available"
  ok=0
fi

if command -v obsidian >/dev/null 2>&1; then
  if obsidian_version="$(obsidian version 2>/dev/null | head -n 1)" && [[ -n "$obsidian_version" ]]; then
    echo "  OK Obsidian CLI ${obsidian_version}"
  else
    echo "  ERROR Obsidian CLI exists but cannot reach a running Obsidian app"
    ok=0
  fi

  if obsidian commands filter=canvas 2>/dev/null | grep -qx 'canvas:new-file'; then
    echo "  OK Canvas core commands are available"
  else
    echo "  ERROR Canvas core commands are unavailable; enable the Canvas core plugin"
    ok=0
  fi

  active_vault="$(obsidian vault info=path 2>/dev/null | tail -n 1)"
  if [[ -n "$active_vault" && -d "$active_vault/.obsidian" ]]; then
    echo "  OK Active Vault: $active_vault"
  else
    echo "  ERROR Cannot resolve the active Obsidian Vault"
    ok=0
  fi
else
  echo "  ERROR obsidian is not on PATH; enable Obsidian CLI in Settings > General"
  ok=0
fi

if [[ -n "$canvas_path" ]]; then
  if [[ "$canvas_path" != *.canvas ]]; then
    echo "  ERROR Target must use the .canvas extension: $canvas_path"
    ok=0
  elif [[ ! -f "$canvas_path" ]]; then
    echo "  ERROR Canvas file does not exist: $canvas_path"
    ok=0
  else
    probe="$(cd "$(dirname "$canvas_path")" && pwd -P)"
    vault_root=""
    while [[ "$probe" != "/" ]]; do
      if [[ -d "$probe/.obsidian" ]]; then
        vault_root="$probe"
        break
      fi
      probe="$(dirname "$probe")"
    done
    if [[ -n "$vault_root" ]]; then
      registered_name="$(obsidian vaults verbose 2>/dev/null | awk -F '\t' -v path="$vault_root" '$2 == path {print $1; exit}')"
      if [[ -n "$registered_name" ]]; then
        echo "  OK Canvas belongs to registered Vault: $registered_name ($vault_root)"
      else
        echo "  ERROR Canvas Vault is not registered with Obsidian: $vault_root"
        ok=0
      fi
    else
      echo "  ERROR Canvas is not inside a directory containing .obsidian"
      ok=0
    fi
  fi
fi

if [[ "$ok" -eq 1 ]]; then
  echo "Ready."
else
  echo "Preflight failed."
  exit 1
fi
