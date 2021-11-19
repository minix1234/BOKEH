FROM continuumio/miniconda3

# MAINTAINER mi nix <minix1234 at outlook.com>

# Install the main packages needed to run the docker applications

RUN conda install -y nomkl bokeh numpy pandas

RUN conda install -y -c conda-forge thermo

RUN conda install -y -c conda-forge fluids

RUN mkdir app


WORKDIR /app

# Replaced individual copys (below) with the entire directory copy above
# ----------------------------------------------------------------------
# COPY GASFLOW /app/GASFLOW/
# COPY LIQUIDFLOW /app/LIQUIDFLOW/

COPY . /app/ 



# Install the current directory as a editable python module
# references the setup.py in the main directory

RUN pip install -e .

WORKDIR /app/openet

EXPOSE 5006

# bokeh serve GASFLOW LIQUIDFLOW --port:5006 --allow-websocket-origin=*
#ENTRYPOINT ["bokeh","serve","/app/bokeh/vpc.py","--allow-websocket-origin=*"]


ENTRYPOINT ["bokeh","serve","GASFLOW","LIQUIDFLOW","--allow-websocket-origin=10.118.197.199:5006"]

#ENTRYPOINT ["bin/bash"]