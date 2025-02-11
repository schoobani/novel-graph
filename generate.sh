#!/bin/bash

GRAPH_ENV=$1
python3 generate.py "$GRAPH_ENV"
python3 build_graph.py "$GRAPH_ENV"