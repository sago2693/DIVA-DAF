<div align="center">

# Your Project Name

<a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>
<a href="https://pytorchlightning.ai/"><img alt="Lightning" src="https://img.shields.io/badge/-Lightning-792ee5"></a>
<a href="https://hydra.cc/"><img alt="Config: Hydra" src="https://img.shields.io/badge/Config-Hydra-89b8cd"></a>
<a href="https://github.com/ashleve/lightning-hydra-template"><img alt="Template" src="https://img.shields.io/badge/-Lightning--Hydra--Template-017F2F?style=flat&logo=github&labelColor=gray"></a><br>

[comment]: <> ([![Paper]&#40;http://img.shields.io/badge/paper-arxiv.1001.2234-B31B1B.svg&#41;]&#40;https://www.nature.com/articles/nature14539&#41;)

[comment]: <> ([![Conference]&#40;http://img.shields.io/badge/AnyConference-year-4b44ce.svg&#41;]&#40;https://papers.nips.cc/paper/2020&#41;)

</div>

## Description
What it does

## How to run
Install dependencies
```yaml
# clone project
git clone https://github.com/DIVA-DIA/unsupervised_learning.git
cd unsupervised_learing

# create conda environment (IMPORTANT: needs Python 3.8+)
conda env create -f conda_env_gpu.yaml

# activate the environment using .autoenv
source .autoenv

# install requirements
pip install -r requirements.txt
```

Train model with default configuration.
Care: you need to change the value of `data_dir` in `config/datamodule/cb55_10_cropped_datamodule.yaml`.
```yaml
# default run based on config/config.yaml
python run.py

# train on CPU
python run.py trainer.gpus=0

# train on GPU
python run.py trainer.gpus=1
```

Train using GPU
```yaml
# [default] train on all available GPUs
python run.py trainer.gpus=-1

# train on one GPU
python run.py trainer.gpus=1

# train on two GPUs
python run.py trainer.gpus=2

# train on CPU
python run.py trainer.accelerator=ddp_cpu
```

Train using CPU for debugging
```yaml
# train on CPU
python run.py trainer.accelerator=ddp_cpu trainer.precision=32
```

Train model with chosen experiment configuration from [configs/experiment/](configs/experiment/)
```yaml
python run.py +experiment=experiment_name
```

You can override any parameter from command line like this
```yaml
python run.py trainer.max_epochs=20 datamodule.batch_size=64
```

<br>
