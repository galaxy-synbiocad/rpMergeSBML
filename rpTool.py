#!/usr/bin/env python3

import libsbml
import argparse

import io
import tarfile
import tempfile
#HDD sepcific
import os
import random
import glob
import string
import logging

import sys #exit using sys exit if any error is encountered
sys.path.insert(0, '/home/')
import rpSBML

logging.disable(logging.INFO)
logging.disable(logging.WARNING)

##
#
#
def mergeSBML_mem(input_tar,
                  target_sbml,
                  output_tar,
                  species_group_id='central_species',
                  sink_species_group_id='rp_sink_species'):
    #loop through all of them and run FBA on them
    with tarfile.open(output_tar, 'w:gz') as tf:
        with tarfile.open(input_tar, 'r') as in_tf:
            for member in in_tf.getmembers():
                if not member.name=='':
                    data = singleMerge_mem(member.name, 
                                           in_tf.extractfile(member).read().decode("utf-8"), 
                                           target_sbml,
                                           pathway_id,
                                           fillOrphanSpecies,
                                           compartment_id)
                    file_name = member.name.replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                    rpsbml = rpSBML.rpSBML(file_name, libsbml.readSBMLFromString(
                            in_tf.extractfile(member).read().decode('utf-8')))
                    target_rpsbml = rpSBML.rpSBML(file_name, libsbml.readSBMLFromFile(target_sbml))
                    rpsbml.mergeModels(target_rpsbml, species_group_id, sink_species_group_id)
                    fiOut = io.BytesIO(libsbml.writeSBMLToString(target_rpsbml.document).encode('utf-8'))
                    info = tarfile.TarInfo(file_name+'_merged.sbml.xml')
                    info.size = len(data)
                    tf.addfile(tarinfo=info, fileobj=fiOut)


##
#
#
def mergeSBML_hdd(input_tar,
                  target_sbml,
                  output_tar,
                  species_group_id='central_species',
                  sink_species_group_id='rp_sink_species'):
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            tar = tarfile.open(input_tar, 'r')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            if len(glob.glob(tmpInputFolder+'/*'))==0:
                logging.error('Input file is empty')
                return False
            for sbml_path in glob.glob(tmpInputFolder+'/*'):
                file_name = sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                rpsbml = rpSBML.rpSBML(file_name)
                rpsbml.readSBML(sbml_path)
                target_rpsbml = rpSBML.rpSBML(file_name)
                target_rpsbml.readSBML(target_sbml)
                rpsbml.mergeModels(target_rpsbml, species_group_id, sink_species_group_id)
                target_rpsbml.writeSBML(tmpOutputFolder)
            if len(glob.glob(tmpOutputFolder+'/*'))==0:
                logging.error('rpMergeSBML has generated no results')
                return False
            with tarfile.open(output_tar, mode='w:gz') as ot:
                for sbml_path in glob.glob(tmpOutputFolder+'/*'):
                    file_name = str(sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', ''))
                    info = tarfile.TarInfo(file_name+'_merged.sbml.xml')
                    info.size = os.path.getsize(sbml_path)
                    ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))
    return True
