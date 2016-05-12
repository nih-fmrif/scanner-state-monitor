
FROM opensuse:13.2

# Command to add needed repos:

RUN zypper ar -f http://download.opensuse.org/update/13.2/ update   &&   \
    zypper ar -f http://ftp.gwdg.de/pub/linux/packman/suse/openSUSE_13.2/ packman   &&   \
    zypper ar -f http://download.opensuse.org/repositories/Education/openSUSE_13.2/ education   &&   \
    zypper ar -f http://download.opensuse.org/repositories/devel:/languages:/python/openSUSE_13.2/ obsPython



# Add rtadmin and meduser/sdc users:

RUN useradd -b /home -d /home/rtadmin -m -u  999 -g 100 -G users,audio -s /bin/bash rtadmin

RUN useradd -b /home -d /home/meduser -m -u 1000 -g 100 -G users,audio -s /bin/bash meduser



# To install AFNI libraries:

# krb5-mini conflicts with samba installation
RUN zypper --gpg-auto-import-keys --non-interactive   remove   krb5-mini

RUN zypper --gpg-auto-import-keys --non-interactive install \
                                     libxft-devel libxp-devel libxpm-devel \
                                     libxmu-devel libpng12-devel libjpeg62 \
                                     zlib-devel libxt-devel libxext-devel \
                                     libexpat-devel netpbm libnetpbm-devel \
                                     libGLU1    vim tar cron which less \
                                     python-numpy python-matplotlib python-dicom \
                                     dcmtk libdcmtk3_6 kradview samba ntp \
                                     wget cmake gcc gcc-c++

ADD ntp.conf                  /etc
ADD smb.conf                  /etc/samba

ADD .afnirc                   /home/rtadmin
ADD rtadmin.bashrc            /home/rtadmin/.bashrc
ADD rtadmin.profile           /home/rtadmin/.profile
RUN mkdir -p                  /home/rtadmin/RTafni/src
RUN mkdir -p                  /home/rtadmin/RTafni/bin
ADD getBuildInstallGDCM.sh    /home/rtadmin/RTafni/src
RUN chown -R rtadmin:users    /home/rtadmin
ADD .startup                  /root

# Allow Siemens console access to the Samba shares
RUN smbpasswd -L -n -a meduser



# Location for volume from host to be mounted in container

VOLUME ["/data0"]



# Ports on container to be exposed/passed through to host

# #        nmbd         smbd      smbd      smbd
# EXPOSE   138:138/udp  139:139   445:445   445:445/udp



# Start up Samba services using default command to run at container startup
ENTRYPOINT ["/bin/bash", "/root/.startup"]

