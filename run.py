#!/usr/bin/env python3
"""
Created on March 17 2020

@author: Melchior du Lac
@description: Merge two SBML together

"""
import argparse
import tempfile
import os
import logging
import shutil
import docker


def main(sourcefile,
         inout_format,
         target_sbml,
         output):
    """Merge two SBML files or a collection of SBML files in the form of a TAR and another SBML file

    :param sourcefile: The path of the TAR or SBML input containing the SBML file
    :param inout_format: The format input of the source (Valid Options: [tar, sbml])
    :param target_sbml: The path of the SBML file to merge to
    :param output: The path to the output file

    :type sourcefile: str
    :type inout_format: str
    :type target_sbml: str
    :type output: str

    :rtype: None
    :return: None
    """
    docker_client = docker.from_env()
    image_str = 'brsynth/rpmergesbml-standalone:v2'
    try:
        image = docker_client.images.get(image_str)
    except docker.errors.ImageNotFound:
        logging.warning('Could not find the image, trying to pull it')
        try:
            docker_client.images.pull(image_str)
            image = docker_client.images.get(image_str)
        except docker.errors.ImageNotFound:
            logging.error('Cannot pull image: '+str(image_str))
            exit(1)
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        if os.path.exists(sourcefile) or os.path.exists(target_sbml):
            shutil.copy(sourcefile, tmpOutputFolder+'/input.dat')
            shutil.copy(target_sbml, tmpOutputFolder+'/target_sbml.dat')
            command = ['python',
                       '/home/tool_rpMergeSBML.py',
                       '-target_sbml',
                       '/home/tmp_output/target_sbml.dat',
                       '-sourcefile',
                       '/home/tmp_output/input.dat',
                       '-inout_format',
                       str(inout_format),
                       '-output',
                       '/home/tmp_output/output.dat']
            container = docker_client.containers.run(image_str,
                                                     command,
                                                     detach=True,
                                                     stderr=True,
                                                     volumes={tmpOutputFolder+'/': {'bind': '/home/tmp_output', 'mode': 'rw'}})
            container.wait()
            err = container.logs(stdout=False, stderr=True)
            err_str = err.decode('utf-8')
            print(err_str)
            if 'ERROR' in err_str:
                print(err_str)
            elif 'WARNING' in err_str:
                print(err_str)
            if not os.path.exists(tmpOutputFolder+'/output.dat'):
                print('ERROR: Cannot find the output file: '+str(tmpOutputFolder+'/output.dat'))
            else:
                shutil.copy(tmpOutputFolder+'/output.dat', output)
            container.remove()
        else:
            logging.error('Cannot find one or both of these files: '+str(sourcefile)+' or '+str(target_sbml))
            exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Convert the results of RP2 and rp2paths to SBML files')
    parser.add_argument('-target_sbml', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-inout_format', type=str)
    params = parser.parse_args()
    main(params.sourcefile,
         params.inout_format,
         params.target_sbml,
         params.output)
