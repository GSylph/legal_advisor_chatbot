#!/usr/bin/env bash
# Deploy to Hugging Face Spaces.
# Strips binary files (PDFs, images) from history before pushing,
# since HF Spaces rejects binary files and requires Xet storage.
#
# Usage: ./deploy-hf.sh

set -euo pipefail

HF_REMOTE="https://GSylph@huggingface.co/spaces/GSylph/ealai"
BRANCH="hf-deploy"

echo "==> Creating clean orphan branch..."
git checkout --orphan "$BRANCH"

echo "==> Staging all files..."
git add -A

echo "==> Removing binary files from this branch..."
git rm -r --cached corpus/ paper/EALAI_Project_Report.pdf paper/figures/ 2>/dev/null || true

echo "==> Committing..."
git commit -m "deploy: $(date '+%Y-%m-%d %H:%M')"

echo "==> Pushing to HF Spaces..."
git push "$HF_REMOTE" "$BRANCH:main" --force

echo "==> Cleaning up..."
git checkout -f main
git branch -D "$BRANCH"

echo "==> Done. Check https://huggingface.co/spaces/GSylph/ealai for build status."
