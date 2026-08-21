#!/bin/bash
/module/scripts/utils/handle_certs.sh
git config --global --add safe.directory "${CI_PROJECT_DIR}"
git -C "${CI_PROJECT_DIR}" remote remove origin 2>/dev/null || true
python3 /module/scripts/utils/sparse_checkout.py
if [[ -f "${HOME}/.bashrc" ]]; then
  source "${HOME}/.bashrc"
fi
python3 /module/scripts/pipeline/orchestrator.py
set -a && . envgene-vars.env && set +a

if [[ "${PIPELINE_TYPE}" == "GITLAB_DEPLOY" ]]; then
  if [[ "${OPERATION_TYPE}" != "CLEAN" ]]; then
    python3 /python/argocd-dpg/src/argo/main.py generate structure \
      -p params.environment_id="${FULL_ENV_NAME}" \
      -p params.deployment_plan="${CI_PROJECT_DIR}/environments/${CLUSTER_NAME}/${ENVIRONMENT_NAME}/Inventory/deploy-plan.yml"
    if [[ -v ENVGENE_AGE_PUBLIC_KEY ]]; then
      sops --encrypt -i --age "${ENVGENE_AGE_PUBLIC_KEY}" ARGO_DPG_CONTEXT.env
    else
      echo "Skipping argo-dpg context encryption because ENVGENE_AGE_PUBLIC_KEY is not defined"
    fi
  fi
  if [[ "${OPERATION_TYPE}" == "CLEAN" ]]; then
    export ESPUSHER_OVERWRITE="true"
  else
    export ESPUSHER_OVERWRITE="false"
  fi
  python3 /python/es-pusher/src/espusher/main.py push \
    -p params.environment_id="${FULL_ENV_NAME}" \
    -p params.commit_message="DEVOPS-001 Push effective set for \"${FULL_ENV_NAME}\"" \
    -p params.overwrite="${ESPUSHER_OVERWRITE}"
fi

if [[ "${PIPELINE_TYPE}" != "GITLAB_DEPLOY" && "${CMDB_IMPORT}" == "true" ]]; then
  /module/scripts/cmdb_import/cmdb_import.sh
fi
