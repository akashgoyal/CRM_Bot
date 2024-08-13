#### setup GCP
sudo apt update
sudo apt install python3 python3-dev
sudo apt-get install wget
sudo apt-get install tmux unzip

mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh

~/miniconda3/bin/conda init bash

conda create -n py310 python=3.10
