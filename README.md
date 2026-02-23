# Figures from Dickman, U., et al. (2026)

1. Download the SNNAP simulation data from [Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.1c59zw488) and make note of the download location.
2. Download [NEURONpyxl](https://github.com/CWRUChielLab/neuronpyxl) and change into the *neuronpyxl* folder. Install the neuronpyxl package into a virtual Python environment:
    - With [uv](https://docs.astral.sh/uv/) (*recommended*):
    `uv venv /path/to/venv --python 3.13 && source /path/to/venv/bin/activate && uv pip install .`
    - With [Micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) (*recommended*): `micromamba create -f environment.yml`
    - With [pip](https://pypi.org/project/pip/):
    `python3 -m venv /path/to/venv && source /path/to/venv/bin/activate && pip install .`
    - With [Anaconda](https://www.anaconda.com/download): `conda create -f environment.yml`
3. Activate NEURONpyxl:
    - With uv or pip: `source /path/to/venv/bin/activate`
    - With Micromamba: `micromamba activate neuronpyxl`
    - With Anaconda: `conda activate neuronpyxl`
4. Run a script from the *./scripts* folder, passing in the script name and location of the Dryad data as arguments. Remember, you first need to compile the mod files for that script. For example
    
    ```
    neuronpyxl -f gen_mods --file sheets/fig2.xlsx && \
    python run_script.py --name fig2 --snnap_data /path/to/snnap/data
    ```
    
    ```
    neuronpyxl -f gen_mods --file sheets/benchmark.xlsx && \
    python run_script.py --name benchmark --snnap_data /path/to/snnap/data
    ```