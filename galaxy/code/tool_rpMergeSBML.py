#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpReader REST service

"""
import sys
sys.path.insert(0, '/home/')
import argparse
import logging
import os
import rpToolServe

##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to merge two SBML files together. The source and target refers to the species and reactions that will be overwritten where the source species will be read first and not overwritten if that species already exists in the target SBML')
    parser.add_argument('-source', type=str)
    parser.add_argument('-inout_format', type=str, choices=['tar', 'sbml'], default='tar')
    parser.add_argument('-target_sbml', type=str)
    parser.add_argument('-output', type=str)
    params = parser.parse_args()
    rpToolServe.main(params.source,
                     params.inout_format,
                     params.target_sbml,
                     params.output)
