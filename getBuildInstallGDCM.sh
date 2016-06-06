
#!/bin/sh

defaultVersionGDCM=2.4.4

if [ "$1" = "-h" -o "$1" = "-help" -o "$1" = "--h" -o "$1" == "--help" ]
then
   echo
   echo "   This script can take only a single argument - the version of GDCM required."
   echo
   echo "      Default is $defaultVersionGDCM"
   echo
   exit 0
fi

if [ $# -lt 1 ]
then
   gdcmVer=$defaultVersionGDCM
else
   gdcmVer=$1
fi

wget http://downloads.sourceforge.net/project/gdcm/gdcm%202.x/GDCM%20$gdcmVer/gdcm-$gdcmVer\.tar.gz

tar xfz gdcm-$gdcmVer\.tar.gz

mkdir gdcm-build-$gdcmVer

cd    gdcm-build-$gdcmVer

cmake -DCMAKE_INSTALL_PREFIX:PATH=/home/rtadmin/RTafni \
      -DGDCM_BUILD_APPLICATIONS:BOOL=ON \
      -DGDCM_BUILD_SHARED_LIBS:BOOL=ON \
      -DGDCM_BUILD_TESTING:BOOL=OFF `find .. -maxdepth 1 -type d -name "gdcm-$gdcmVer*"`

make && make install

