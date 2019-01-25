#!/bin/bash -xe

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [[ -z "$1" ]]; then
    echo "usage $0 channel"
    exit 1
fi

CHANNEL=$1
VERSION=$(curl http://apps.syncloud.org/releases/${CHANNEL}/snapd.version)
ARCH=$(dpkg --print-architecture)

SNAPD=snapd-${VERSION}-${ARCH}.tar.gz

cd /tmp
rm -rf ${SNAPD}
rm -rf snapd

wget http://apps.syncloud.org/apps/${SNAPD} --progress=dot:giga
tar xzvf ${SNAPD}
systemctl stop snapd.service snapd.socket || true
#systemctl disable snapd.service snapd.socket || true

cp snapd/bin/snapd /usr/lib/snapd
cp snapd/bin/snap-exec /usr/lib/snapd
cp snapd/bin/snap-confine /usr/lib/snapd
cp snapd/bin/snap-seccomp /usr/lib/snapd
cp snapd/bin/snap-repair /usr/lib/snapd
cp snapd/bin/snap-update-ns /usr/lib/snapd
cp snapd/bin/snap-discard-ns /usr/lib/snapd
cp snapd/bin/snap /usr/bin
cp snapd/bin/snapctl /usr/bin
cp snapd/bin/mksquashfs /usr/bin
cp snapd/bin/unsquashfs /usr/bin
cp snapd/lib/* /lib/$HOSTTYPE-$OSTYPE

cp snapd/conf/snapd.service /lib/systemd/system/
cp snapd/conf/snapd.socket /lib/systemd/system/

#systemctl enable snapd.service
#systemctl enable snapd.socket
systemctl start snapd.service snapd.socket

