#!/bin/bash

GRAPH_ENV=$1
python3 src/generate.py "$GRAPH_ENV"
python3 src/build_graph.py "$GRAPH_ENV"