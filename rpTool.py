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

import sys #exit using sys exit if any error is encountered
sys.path.insert(0, '/home/')
import rpSBML


##
#
#
def mergeSBML_mem(input_tar, target_sbml, output_tar):
    #loop through all of them and run FBA on them
    with tarfile.open(output_tar, 'w:xz') as tf:
        with tarfile.open(input_tar, 'r:xz') as in_tf:
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
                    rpsbml.mergeModels(target_rpsbml)
                    fiOut = io.BytesIO(libsbml.writeSBMLToString(target_rpsbml.document).encode('utf-8'))
                    info = tarfile.TarInfo(file_name+'_merged.sbml.xml')
                    info.size = len(data)
                    tf.addfile(tarinfo=info, fileobj=fiOut)


##
#
#
def mergeSBML_hdd(input_tar, target_sbml, output_tar):
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            tar = tarfile.open(input_tar, 'r:xz')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            for sbml_path in glob.glob(tmpInputFolder+'/*'):
                file_name = sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', '')
                rpsbml = rpSBML.rpSBML(file_name)
                rpsbml.readSBML(sbml_path)
                target_rpsbml = rpSBML.rpSBML(file_name)
                target_rpsbml.readSBML(target_sbml)
                rpsbml.mergeModels(target_rpsbml)
                target_rpsbml.writeSBML(tmpOutputFolder)
            with tarfile.open(output_tar, mode='w:xz') as ot:
                for sbml_path in glob.glob(tmpOutputFolder+'/*'):
                    file_name = str(sbml_path.split('/')[-1].replace('.sbml', '').replace('.xml', '').replace('.rpsbml', ''))
                    info = tarfile.TarInfo(file_name+'_merged.sbml.xml')
                    info.size = os.path.getsize(sbml_path)
                    ot.addfile(tarinfo=info, fileobj=open(sbml_path, 'rb'))
