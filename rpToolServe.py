#!/usr/bin/env python3

import sys
import logging
import tempfile
import tarfile
import os
import shutil
import glob

sys.path.insert(0, '/home/')
import inchikeyMIRIAM
import rpTool
import rpCache

logging.basicConfig(
    #level=logging.DEBUG,
    level=logging.WARNING,
    #level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)

def main(source,
         inout_format,
         target_sbml,
         output):
    """Merge one or more SBML files together

    :param source: The path of the TAR or SBML input containing the SBML file
    :param inout_format: The format input of the source (Valid Options: [tar, sbml])
    :param target_sbml: The path of the SBML file to merge to
    :param output: The path of the TAR or SBML output file

    :type source: str
    :type inout_tar: str
    :type target_sbml: str
    :type output: str

    :rtype: None
    :return: None
    """
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        if inout_format=='tar':
            inchikey_enriched_target_sbml = os.path.join(tmpInputFolder, 'tmp.sbml')
            inchikeyMIRIAM.main(target_sbml, inchikey_enriched_target_sbml)
            rpTool.mergeSBML_hdd(source,
                                 inchikey_enriched_target_sbml,
                                 output)
        elif inout_format=='sbml':
            inchikey_enriched_target_sbml = os.path.join(tmpInputFolder, 'target_tmp.sbml')
            inchikeyMIRIAM.main(target_sbml, inchikey_enriched_target_sbml)
            inchikey_enriched_source_sbml = os.path.join(tmpInputFolder, 'source_tmp.sbml')
            inchikeyMIRIAM.main(source, inchikey_enriched_source_sbml)
            with tempfile.TemporaryDirectory() as tmpOutputFolder:
                inputTar = tmpOutputFolder+'/tmp_input.tar'
                outputTar = tmpOutputFolder+'/tmp_output.tar'
                with tarfile.open(inputTar, mode='w:gz') as tf:
                    info = tarfile.TarInfo('single.sbml.xml') #need to change the name since galaxy creates .dat files
                    info.size = os.path.getsize(inchikey_enriched_source_sbml)
                    tf.addfile(tarinfo=info, fileobj=open(source, 'rb'))
                rpTool.mergeSBML_hdd(inputTar,
                                     inchikey_enriched_target_sbml,
                                     outputTar)
                with tarfile.open(outputTar) as outTar:
                    outTar.extractall(tmpOutputFolder)
                out_file = glob.glob(tmpOutputFolder+'/*.xml')
                if len(out_file)>1:
                    logging.warning('There are more than one output file...')
                shutil.copy(out_file[0], output)
        else:
            logging.error('Cannot identify the input/output format: '+str(inout_format))
