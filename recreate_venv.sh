#!/bin/bash
# Python 3.12 で仮想環境を作り直すスクリプト
# 使い方: Python 3.12 をインストールしたあと、./recreate_venv.sh を実行

set -e
cd "$(dirname "$0")"

if [ -x "/usr/local/bin/python3.12" ]; then
  PYTHON312="/usr/local/bin/python3.12"
elif command -v python3.12 &>/dev/null; then
  PYTHON312="python3.12"
else
  PYTHON312=""
fi
if [ -z "$PYTHON312" ] || ! [ -x "$PYTHON312" ]; then
  echo "Python 3.12 が見つかりません。公式インストーラーでインストールしてください。"
  echo "  https://www.python.org/downloads/release/python-31210/"
  exit 1
fi

echo "使用する Python: $($PYTHON312 --version)"
echo "既存の .venv を削除しています..."
rm -rf .venv
echo "新しい仮想環境を作成しています..."
"$PYTHON312" -m venv .venv
echo "完了。有効化: source .venv/bin/activate"
