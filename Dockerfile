FROM python:3.13.5-slim
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        git \
        gnupg2 &&\
    apt-get clean &&\
    curl -k -L -o jdk-24_linux-x64_bin.tar.gz https://download.oracle.com/java/24/archive/jdk-24.0.1_linux-x64_bin.tar.gz &&\
    tar -xzf jdk-24_linux-x64_bin.tar.gz &&\
    rm jdk-24_linux-x64_bin.tar.gz
    
# Copy Nextflow binary from the builder stage
COPY --from=nextflow/nextflow:25.04.6 /usr/local/bin/nextflow /usr/local/bin/nextflow
RUN chmod 755 /usr/local/bin/nextflow
ENV PATH="/root/.nextflow:/jdk-24.0.1/bin:${PATH}"
ENV NXF_HOME="/root/.nextflow"

RUN mkdir -p /root/.nextflow/framework/25.04.6 &&\
    curl -k -L -o  \
        /root/.nextflow/framework/25.04.6/nextflow-25.04.6-one.jar \
        https://www.nextflow.io/releases/v25.04.6/nextflow-25.04.6-one.jar &&\
    nextflow -version &&\
    nextflow plugin install nf-azure@1.3.3 &&\
    nextflow plugin install nf-weblog@1.1.2 &&\
    nextflow plugin install nf-schema@2.1.1 &&\
    curl -k -L -o azcopy.tar.gz https://aka.ms/downloadazcopy-v10-linux && \     
     tar zxvf azcopy.tar.gz --strip-components=1 && \
     rm azcopy.tar.gz && \     
     chmod +x azcopy && \     
     mv azcopy /usr/local/bin/azcopy


# setup process code
COPY main.nf submission_config.yml /
RUN mkdir -p /temp/src
WORKDIR /temp
COPY src /temp/src
COPY pyproject.toml README.md /temp/
RUN pip install .
WORKDIR /
RUN rm -rf /temp
