#!/bin/sh
# ENG HUB - Pardus / Linux launcher
# Cift tiklayin veya:  ./start-pardus.sh

cd "$(dirname "$0")" || exit 1

echo
echo "  ==========================================="
echo "    ENG HUB  -  baslatiliyor / starting..."
echo "  ==========================================="
echo

find_python() {
    for cand in ./runtime/python-linux/bin/python3 python3 python; do
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
    echo "  Bu bilgisayarda Python 3 bulunamadi."
    echo "  No Python 3 found on this computer."
    echo
    printf "  Simdi kurulsun mu? (yonetici parolasi gerekir) [e/H]: "
    read -r answer
    case "$answer" in
        e|E|y|Y)
            if command -v apt >/dev/null 2>&1; then
                sudo apt update && sudo apt install -y python3
            elif command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3
            elif command -v pacman >/dev/null 2>&1; then
                sudo pacman -S --noconfirm python
            else
                echo "  Paket yoneticisi bulunamadi. Python 3'u elle kurun."
            fi
            PYEXE=$(find_python)
            ;;
    esac
fi

if [ -z "$PYEXE" ]; then
    echo
    echo "  Python olmadan ENG HUB baslatilamaz."
    echo "  Kurulum:  sudo apt install python3"
    echo
    printf "  Kapatmak icin Enter'a basin..."
    read -r _
    exit 1
fi

echo "  Python: $PYEXE"
echo
"$PYEXE" ./server/enghub.py

echo
echo "  ENG HUB kapandi."
