# Overview

````bash
    docker build . -t mcrl2-lts
```

```bash
    docker run -it --mount type=bind,source=./output/,target=/root/output mcrl2-lts
```

````bash
    python3 /root/scripts/generate.py /root/mCRL2/build/stage/bin /root/cases/ /root/output/
```