<h1 align="center">FireWorks/Atomate Tutorial</h1>

**:warning: WARNING:** This tutorial does not provide any licensed code or file.

## Introduction
[FireWorks](https://materialsproject.github.io/fireworks/) is a free, open-source code for defining, managing, and executing scientific workflows. It can be used to automate calculations over arbitrary computing resources, including those that have a queueing system.

[Atomate](https://atomate.org) makes it possible to perform complex materials science computations using very straightforward statements.

[Pymatgen](https://pymatgen.org) is a robust, open-source Python library for materials analysis.

## Content

- `fireworks_tutorial.ipynb`: Basic introduction to FireWorks with simple examples from their documentation.

- `fireworks_tutorial_vasp.ipynb`: FireWorks/Atomate tutorial for materials science (VASP).

- `fireworks_tutorial_fakevasp.ipynb`: Same tutorial but using RunFakeVasp (FireTask) instead of VASP code.

- `src/analysis.py`: Custome analysis firetasks (e.g `PlotEncutCalib`, `FitEOSTask`, etc.)

- `src/dft_settings.py`: General DFT settings for the tutorial.

- `src/reference_dirs.py`: Directories for FakeVasp and custome Fireworks `OptimizeFakeFW` and `TransmutterFakeFW`.

## Citation

There is no citation! Feel free to fork (:fork_and_knife:) and leave a start (:star:)
