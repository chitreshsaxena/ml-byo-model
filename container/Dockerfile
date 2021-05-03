FROM debian:buster-slim
ARG XGBOOST_VERSION=1.2.0
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

ENV PATH /opt/conda/bin:$PATH

ENV PATH /opt/conda/envs/AWSBatch/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 git mercurial subversion && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    /opt/conda/bin/conda clean -afys

# Install latest version of XGBoost
RUN python3 -m pip install --no-cache -I xgboost==${XGBOOST_VERSION}

RUN conda update -n base -c defaults conda

COPY environment.yml /

RUN conda env create -f environment.yml

RUN conda clean -tp -y

RUN echo "source activate AWSBatch" > ~/.bashrc

COPY batch_processor.py /

CMD ["python", "batch_processor.py"]
