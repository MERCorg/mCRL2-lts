# Overview

This repository contains a collection of mCRL2 case studies along with scripts
to generate their corresponding labeled transition systems (LTSs). The goal is
to provide a diverse set of large LTSs for benchmarking and research purposes.

We use [Docker](https://www.docker.com/) to provide a reproducible environment
for generating the LTSs, especially since the compiling rewriter is not avaiable
on Windows. The Docker image can be built using the following command:

```bash
docker build . -t mcrl2-lts
```

Afterwards, we mount the `cases` and `output` directories into the container.
This is done because the output is rather large, so we only want to store it on
the host machine.

```bash
docker run -it --mount type=bind,source=./output/,target=/root/output --mount type=bind,source=./cases/,target=/root/cases mcrl2-lts
```

Inside the container, we can run the generation script as follows:

```bash
python3 /root/scripts/generate.py /root/mCRL2/build/stage/bin /root/cases/ /root/output/
```

This will produce the output LTSs in the `output` directory on the host machine,
in compressed `.aut.bz2` format to save space. Furthermore, a summary file
`summary.json` will be created containing information about each generated LTS.