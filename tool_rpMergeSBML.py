#!/usr/bin/env python3

import glob
import tarfile
import argparse
import shutil
import os
import tempfile

import sys #exit using sys exit if any error is encountered
sys.path.insert(0, '/home/')
import rpTool

##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Given a collection of sbml files as a tar.xz and a SBML files, merge the two and output the results in a tar.xz')
    parser.add_argument('-target_sbml', type=str)
    parser.add_argument('-input', type=str)
    parser.add_argument('-input_format', type=str)
    parser.add_argument('-output', type=str)
    params = parser.parse_args()
    if params.input_format=='tar': 
        rpTool.mergeSBML_hdd(params.input, params.target_sbml, params.output)
    elif params.input_format=='sbml': 
        #make the tar.xz 
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            input_tar = tmpOutputFolder+'/tmp_input.tar.xz'
            output_tar = tmpOutputFolder+'/tmp_output.tar.xz'
            with tarfile.open(input_tar, mode='w:xz') as tf:
                info = tarfile.TarInfo('single.rpsbml.xml')
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
            rpTool.mergeSBML_hdd(input_tar, params.target_sbml, output_tar)
            with tarfile.open(output_tar) as outTar:
                outTar.extractall(tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.sbml.xml')
            if len(out_file)>1:
                logging.warning('There are more than one output file...')
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot have no SBML and no TAR input')
        exit(0)
