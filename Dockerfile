FROM oraclelinux:7-slim

RUN  yum -y install oracle-release-el7 && \
     yum -y install oracle-epel-release-el7 && \
     yum-config-manager --enable ol7_optional_latest && \
     yum -y install oracle-instantclient19.3-basiclite && \
     yum -y install gcc gcc-c++ openssl-devel bzip2-devel libffi-devel autoconf automake && \
     yum -y install python3 python3-libs python3-devel && \
     rm -rf /var/cache/yum

ADD . /function
WORKDIR /function

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --target /python/  --no-cache --no-cache-dir -r requirements.txt
RUN rm -fr ~/.cache/pip /tmp* requirements.txt func.yaml Dockerfile .venv
ENV PYTHONPATH=/python

ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]