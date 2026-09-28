#!/bin/bash
set -e
clear
echo "FlowLogue — Apple Notes Exporter"
echo
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/ZunagesCo/flowlogue-public/main/tools/apple-notes-exporter/install.sh)"
echo
read -n 1 -s -r -p "Press any key to close..."
echo
