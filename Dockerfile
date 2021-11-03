FROM continuumio/miniconda3

#MAINTAINER Antonia Elek <antoniaelek at hotmail.com>

RUN conda install -y nomkl bokeh numpy pandas

RUN conda install -y -c conda-forge thermo

RUN conda install -y -c conda-forge fluids

RUN mkdir app

WORKDIR /app

COPY GASFLOW /app/GASFLOW/
COPY LIQUIDFLOW /app/LIQUIDFLOW/

EXPOSE 5006

# bokeh serve GASFLOW LIQUIDFLOW --port:5006 --allow-websocket-origin=*
#ENTRYPOINT ["bokeh","serve","/app/bokeh/vpc.py","--allow-websocket-origin=*"]


ENTRYPOINT ["bokeh","serve","GASFLOW","LIQUIDFLOW","--allow-websocket-origin=10.118.197.199:5006"]

#ENTRYPOINT ["bin/bash"]