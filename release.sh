#!/bin/bash

set -eu
set -o pipefail

# Release the new version of QC-ETL
git update-index --refresh
if ! git diff-index --quiet HEAD; then
	echo "There are changes to tracked files. Please deal with these before resuming the release."
	exit 2
fi
git fetch origin
git checkout origin/main
OLD_VERSION="$(uv version --short)"

read -e -p "Please enter the new version (current version is ${OLD_VERSION}): " -i "${OLD_VERSION}" NEW_VERSION
if git tag --list | grep -c -E "^v${NEW_VERSION}$" > /dev/null; then
  echo "Version $NEW_VERSION already exists. Please restart and select a different version number."
	exit 3
fi

if ! grep -q "[Unreleased]" CHANGELOG.md; then
    echo "Error: changelog does not contain an [Unreleased] section"
    exit 4
fi
## show changelog and verify that it is correct
sed -n '/## \[Unreleased\]/,/## \[/{ /## /d; p }' CHANGELOG.md
read -r -p "Is this change log correct and complete? [y/N]" RESPONSE
if [[ ! "$RESPONSE" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Release aborted. Please complete the [Unreleased] section of CHANGELOG.md"
    exit 5
fi

DATE=$(date +%Y-%m-%d)
sed -i "s/## \[Unreleased\]/## \[Unreleased\]\n\n## \[${NEW_VERSION}\] - ${DATE}/g" CHANGELOG.md

git checkout -b "v${NEW_VERSION}_pr"

uv version "$NEW_VERSION"

git add pyproject.toml
git add CHANGELOG.md
git commit -m "QC-ETL $NEW_VERSION release"
git tag "v${NEW_VERSION}"

git push -u origin "v${NEW_VERSION}_pr"
git push origin "v${NEW_VERSION}"
echo "Release completed (after the PR has been merged). Copy this export into your shell before running the deploy scripts:"
echo "export QCETL_RELEASE_VERSION=${NEW_VERSION} QCETL_PREVIOUS_VERSION=${OLD_VERSION}"
xdg-open "https://github.com/oicr-gsi/qc-etl/compare/main...v${NEW_VERSION}?quick_pull=1" &
exit 0
