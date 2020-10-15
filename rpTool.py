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
import rpSBML
import rpMerge


def mergeSBML_hdd(input_tar,
                  target_sbml,
                  output_tar)
    """Merge one or more SBML files together

    :param input_tar: The path of the TAR input containing the SBML file
    :param target_sbml: The path of the SBML file to merge to
	:param output_tar: The path of the TAR output file

    :type input_tar: str
    :type target_sbml: str
	:type output_tar: str

    :rtype: bool
    :return: The success or failure of the function
    """	
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
                rpmerge = rpMerge.rpMerge()
				species_source_target, reactions_convert = rpmerge.mergeModels(rpsbml, rpsbml_gem)
				if target_reaction in reactions_convert:
					logging.warning('The target_reaction ('+str(target_reaction)+') has been detected in model '+str(file_name)+', ignoring this model...')
					return False
				rev_reactions_convert = {v: k for k, v in reactions_convert.items()}
				logging.debug('species_source_target: '+str(species_source_target))
				logging.debug('reactions_convert: '+str(reactions_convert))
				logging.debug('rev_reactions_convert: '+str(rev_reactions_convert))
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
