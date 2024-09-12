ARCH=$(uname -m)
if [ "$ARCH" == "aarch" ]; then
    ARCH="arm64"
elif [ "$ARCH" == "amd64" ]; then
    ARCH="x86_64"
fi

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
if [ "$OS" == "darwin" ]; then
    OS="MacOSX"
elif [ "$OS" == "linux" ]; then
    OS="Linux"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

function update() {
  if [ "$OS" == "Linux" ]; then
    sudo apt-get update
  elif [ "$OS" == "MacOSX" ]; then
    brew update
  fi
}

function install() {
  if [ "$OS" == "Linux" ]; then
    sudo apt-get update
    sudo apt-get install -y $@
  elif [ "$OS" == "MacOSX" ]; then
    brew install $@
  fi
}

function pip_install() {
  # check if pip is installed, else check if pip3 is installed otherwise do python3 -m pip
  if command -v pip3 &> /dev/null; then
    pip3 install $@
  elif command -v pip &> /dev/null; then
    pip install $@
  else
    python3 -m pip install $@
  fi
}

install wget curl git

# download and install anaconda in non-interactive mode
wget https://repo.anaconda.com/archive/Anaconda3-2024.06-1-$OS-$ARCH.sh
bash Anaconda3-2024.06-1-$OS-$ARCH.sh -b -p $HOME/anaconda3

# create jupyter dictionaries
mkdir -p $HOME/.jupyter || echo "directory $HOME/.jupyter already exists"
mkdir -p $HOME/Server/jupyter || echo "directory $HOME/Server/jupyter already exists"

# install mlflow
pip_install mlflow


# add labs configuration
cat <<EOF | tee $HOME/.jupyter/jupyter_lab_config.py
c.ServerApp.ip = '0.0.0.0'
EOF

# set up services for linux servers
if [ "$OS" == "Linux" ]; then
cat <<EOF | sudo tee /etc/systemd/system/jupyter.service
[Service]
Type=simple
PIDFile=/run/jupyter.pid
ExecStart=/bin/bash -i -c "conda activate jupyterlab; jupyter lab --config $HOME/.jupyter/jupyter_lab_config.py"
User=$USER
WorkingDirectory=$HOME/Server/jupyter
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/systemd/system/mlflow.service
[Service]
Type=simple
PIDFile=/run/jupyter.pid
ExecStart=/bin/bash -i -c "mlflow server --host 0.0.0.0 --port 8889"
User=$USER
WorkingDirectory=$HOME/Server/jupyter
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

sudo reboot