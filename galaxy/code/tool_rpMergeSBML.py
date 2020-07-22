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
    parser.add_argument('-source_format', type=str, choices=['tar', 'sbml'], default='tar')
    parser.add_argument('-target_sbml', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-species_group_id', type=str, default='central_species')
    parser.add_argument('-sink_species_group_id', type=str, default='rp_sink_species')
    parser.add_argument('-pathway_id', type=str, default='rp_pathway')
    params = parser.parse_args()
    if params.input_format=='tar':
        rpToolServe.main(input_tar,
                        target_sbml,
                        output_tar,
                        params.species_group_id,
                        params.sink_species_group_id,
                        params.pathway_id) 
    elif params.input_format=='sbml':
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            inputTar = tmpOutputFolder+'/tmp_input.tar'
            outputTar = tmpOutputFolder+'/tmp_output.tar'
            with tarfile.open(inputTar, mode='w:gz') as tf:
                info = tarfile.TarInfo('single.sbml.xml') #need to change the name since galaxy creates .dat files
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
            rpToolServe.main(inputTar,
                            target_sbml,
                            outputTar,
                            params.species_group_id,
                            params.sink_species_group_id,
                            params.pathway_id) 
            with tarfile.open(outputTar) as outTar:
                outTar.extractall(tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.sbml.xml')
            if len(out_file)>1:
                logging.warning('There are more than one output file...')
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot identify the input/output format: '+str(params.input_format))
        exit(1)

