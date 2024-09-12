#!/bin/bash

while [[ $# -gt 0 ]]
do
  key="$1"

  case $key in
    --setup)
    git clone https://github.com/mage-ai/mlops.git
    cd mlops
    shift
    ;;
    --start)
    cd mlops
    ./scripts/start.sh
    shift
    ;;
    *)
    # Unknown option
    echo "Unknown option: $key"
    shift
    ;;
  esac
done