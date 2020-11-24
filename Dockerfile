FROM brsynth/rpcache

RUN git clone https://github.com/Galaxy-SynBioCAD/inchikeyMIRIAM.git -b standalone-v2
RUN mv inchikeyMIRIAM/inchikeyMIRIAM.py /home/
RUN rm -r inchikeyMIRIAM

COPY rpTool.py /home/
COPY rpToolServe.py /home/
COPY galaxy/code/tool_rpMergeSBML.py /home/
