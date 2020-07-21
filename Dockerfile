FROM brsynth/rpbase:v1

RUN git clone https://github.com/Galaxy-SynBioCAD/inchikeyMIRIAM.git -b master
RUN mv inchikeyMIRIAM/inchikeyMIRIAM.py /home/
RUN rm -r inchikeyMIRIAM

COPY rpTool.py /home/
COPY tool_rpMergeSBML.py /home/
