#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 app [--include-data]"
    exit 1
fi

APP=$1
INCLUDE_DATA=${1:-no}

STORAGE_DIR=/data
BACKUP_NAME=${APP}_`date +"%Y%m%d_%H%M%S"`
BASE_DIR=${STORAGE_DIR}/platform/backup/${APP}
BACKUP_DIR=${BASE_DIR}/${BACKUP_NAME}

APP_CURRENT_DIR=/var/snap/$APP/current
APP_COMMON_DIR=/var/snap/$APP/common

APP_DATA_DIR=${STORAGE_DIR}/$APP

APP_CURRENT_SIZE=$(du -s ${APP_CURRENT_DIR} | cut -f1)
APP_COMMON_SIZE=$(du -s ${APP_COMMON_DIR} | cut -f1)
APP_DATA_SIZE=0
if [[ "${INCLUDE_DATA}" == "--include-data" ]]; then
    APP_DATA_SIZE=$(du -s ${APP_DATA_DIR} | cut -f1)
fi

STORAGE_SPACE_LEFT=$(df --output=avail ${STORAGE_DIR} | tail -1)
STORAGE_SPACE_NEEDED=$(( ${APP_CURRENT_SIZE} + ${APP_COMMON_SIZE} + ${APP_DATA_SIZE} ))

if [[ ${STORAGE_SPACE_NEEDED} -gt ${STORAGE_SPACE_LEFT} ]]; then
    echo "not enaugh space on ${STORAGE_DIR} (${STORAGE_SPACE_LEFT}) for a backup (${STORAGE_SPACE_NEEDED})"
    exit 1
fi

mkdir -p ${BACKUP_DIR}

snap stop $APP
cp -r ${APP_CURRENT_DIR} ${BACKUP_DIR}
cp -r ${APP_COMMON_DIR} ${BACKUP_DIR}
if [[ "${INCLUDE_DATA}" == "--include-data" ]]; then
    cp -r ${APP_DATA_DIR} ${BACKUP_DIR}
fi
snap start $APP
tar czf ${BASE_DIR}/${BACKUP_NAME}.tar.gz -C ${BASE_DIR} ${BACKUP_NAME}
rm -rf ${BACKUP_DIR}
