#!/bin/sh
# ENG HUB - Pardus / Linux Guncelleme
# Cift tiklayin veya:  ./update-pardus.sh

cd "$(dirname "$0")" || exit 1

APP="."
[ -f ./src/server/enghub.py ] && APP="./src"

find_python() {
    for cand in "$APP/runtime/python-linux/bin/python3" python3 python; do
        if command -v "$cand" >/dev/null 2>&1 || [ -x "$cand" ]; then
            if "$cand" -c 'import sys;sys.exit(0 if sys.version_info>=(3,8) else 1)' >/dev/null 2>&1; then
                echo "$cand"
                return 0
            fi
        fi
    done
    return 1
}

PYEXE=$(find_python)

if [ -z "$PYEXE" ]; then
    echo "  Python 3 bulunamadi."
    echo "  Kurulum: sudo apt install python3"
    printf "  Kapatmak icin Enter'a basin..."
    read -r _
    exit 1
fi

echo "  Python: $PYEXE"
echo "  ENG HUB guncellemeleri denetleniyor..."
echo

if [ -f "$APP/updater.py" ]; then
    "$PYEXE" "$APP/updater.py" "$@"
elif [ -f "./updater.py" ]; then
    "$PYEXE" "./updater.py" "$@"
fi

echo
printf "  Kapatmak icin Enter'a basin..."
read -r _
