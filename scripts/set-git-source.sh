#!/usr/bin/env bash

set -eo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
[[ -n "${DEBUG:-}" ]] && set -x


if [ -z ${GIT_ORG} ]; then
 echo "Please set GIT_ORG when running script, optional GIT_BASEURL and GIT_REPO to formed the git url GIT_BASEURL/GIT_ORG/GIT_REPO"
 exit 1
fi

set -u

GIT_BRANCH=${GIT_BRANCH:-HEAD}
GIT_BASEURL=${GIT_BASEURL:-https://github.com}
GIT_REPO=${GIT_REPO:-eks-blueprints-add-ons}
GIT_BASEDIRL=${GIT_BASEDIR:-argocd}

REPLACE_GIT_REPO_FULL=${REPLACE_GIT_REPO_FULL:-"repoURL: https://github.com/aws-samples/eks-blueprints-add-ons"}
REPLACE_GIT_BRANCH=${REPLACE_GIT_BRANCH:-"targetRevision: HEAD"}

echo "Configuring gitops to use ${GIT_BASEURL}/${GIT_ORG}/${GIT_REPO} on branch ${GIT_BRANCH}"

find ${SCRIPTDIR}/../${GIT_BASEDIRL} -name '*.yaml' -print0 |
  while IFS= read -r -d '' File; do
    if grep -q "kind: Application\|kind: AppProject" "$File"; then
      #echo "$File"
      sed -i'.bak' -e "s#${REPLACE_GIT_REPO_FULL}#repoURL: ${GIT_BASEURL}/${GIT_ORG}/${GIT_REPO}#" $File
      sed -i'.bak' -e "s#${REPLACE_GIT_BRANCH}#targetRevision: ${GIT_BRANCH}#" $File
      rm "${File}.bak"
    fi
  done
echo "done .yaml files"
echo "git commit and push changes now"