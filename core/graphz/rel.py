#!/usr/bin/env python3
# coding: utf-8
import csv
import asyncio
import glob
import json
import os
import time
from typing import Tuple

import graphviz
import pandas as pd
from graphviz import Digraph
from pandas import DataFrame
import openpyxl as ox

from core.common.utils import FolderBase, ReadCombinedFile, find_key


class RelationFile(ReadCombinedFile):
    def openRel(self) -> list:
        mlist = []

        with open(self.file, newline='') as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                address_p = line.split(" - ")
                if address_p[0][:2] == "0x":
                    needle = [f"{address_p[0]}", f"{address_p[1]}"]
                else:
                    needle = [f"0x{address_p[0]}", f"0x{address_p[1]}"]
                if needle not in mlist:
                    mlist.append(needle)
        return mlist


class GraphBuildingBscRelation(FolderBase):
    def __init__(self, project_name: str):
        self.by_project_name(project_name)
        grah_name = f"{project_name}-referrals"
        dot = graphviz.Digraph(
            name=grah_name,
            comment='Sun',
            engine='dot',
            format='pdf'
        )
        dot.attr(
            ordering='out',
            k='2.2',
            overlap='prism0',
            rankdir='LR',
            size='1000,250'
        )
        self.style = {
            "s1": "Mdiamond",
            "s2": "Mcircle",
            "s3": "star",
            "fillcolor": "#459c10",
            "fontcolor": "white",
        }
        self._dot: Digraph = dot

    def bsc_relation_advanced(self, _file: str, name_tags: dict):
        ob = self.style
        addresses = RelationFile(_file).openRel()
        d_count = 0
        container = []
        for from_address in addresses:
            child = from_address[0].lower()
            parent = from_address[1].lower()
            y = find_key(container, parent)
            if y > -1:
                container[y]["children"] += 1
                container[y]["down"].append(child)
            else:
                # container[parent]["children"] = 0
                container.append({
                    "up": parent,
                    "children": 0,
                    "down": [],
                })

        container = sorted(container, key=lambda x: -x["children"])
        linear_nodes = []
        for c in container:
            up = c["up"]
            for dow in c["down"]:
                self._dot.edge(
                    up, dow,
                    labeldistance='1.2',
                    labelangle='30',
                )

                if up not in linear_nodes:
                    linear_nodes.append(up)
                if dow not in linear_nodes:
                    linear_nodes.append(dow)

        for x in linear_nodes:
            if x not in name_tags:
                continue

            name_f = name_tags[x]
            node_label_content = f"{name_f}\n{x}"

            self._dot.node(
                x,
                shape=ob["s1"],
                fillcolor=ob["fillcolor"],
                style="filled",
                fontcolor=ob["fontcolor"],
                gradientangle="270",
                label=node_label_content
            )

    def bsc_relation_read(self, _file: str):
        addresses = RelationFile(_file).openRel()
        d_count = 0
        container = []
        for from_address in addresses:
            child = from_address[0]
            parent = from_address[1]
            y = find_key(container, parent)
            if y > -1:
                container[y]["children"] += 1
                container[y]["down"].append(child)
            else:
                # container[parent]["children"] = 0
                container.append({
                    "up": parent,
                    "children": 0,
                    "down": [],
                })

        container = sorted(container, key=lambda x: -x["children"])

        for c in container:
            up = c["up"]
            for dow in c["down"]:
                self._dot.edge(up, dow)
        # for level in container:
        # dot.edge(parent, child)
        # print(f"The total edges is 0")

    def address_counting(self, file: str) -> Tuple[int, list]:
        addresses = RelationFile(file).openRel()
        container = []

        for from_address in addresses:
            child = from_address[0]
            parent = from_address[1]

            if child not in container:
                container.append(child)
            if parent not in container:
                container.append(parent)

        return (len(container), container)

    def build_relation_graph(self, relation_file_name: str = 'relation.txt'):
        path = os.path.join(self.excelfolder, relation_file_name)
        self.bsc_relation_read(path)
        self._dot.render(directory=self.excelfolder).replace('\\', '/')

    def build_relation_graph_nametagged(self, dat: dict, relation_file_name: str = 'relation.txt'):
        path = os.path.join(self.excelfolder, relation_file_name)
        self.bsc_relation_advanced(path, dat)
        self.count_relations_unique(relation_file_name)
        self._dot.render(directory=self.excelfolder).replace('\\', '/')

    def count_relations_unique(self, relation_file_name: str = 'relation.txt'):
        path = os.path.join(self.excelfolder, relation_file_name)
        (n, collection) = self.address_counting(path)
        print(f"total members: {n}")
