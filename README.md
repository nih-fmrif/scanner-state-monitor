
# Docker image for the FMRIF's Real-Time AFNI Framework

This reposiotry will hold a Docker container build configuration, in
addition to program files to support FMRIF's real-time AFNI framework.

The command to run this container is:

   ```bash
   docker run --name rtAFNI -p 138:138/udp -p 139:139 -p 445:445 -p 445:445/udp -p 8111:8111 \
                            -v /data0/:/data0 -it dockerAcctName/containerName:version
   ```

This will start the container with all of the ports needed for Samba
opened and mapped, and the port chosen for the scanner console to send
messages to, and for the DICOM listener (running in the container) to
observe.

The first time the container is run, the Samba password for the meduser
account must be set, with the command:

   ```bash
   smbpasswd meduser
   ```

and after this, the volume shared by the container (/data0) should be
accessible from the MRI's console computer via Windows File Sharing.

The container's super-user should also switch to the container's
'rtadmin' user, and run:

   ```bash
   cd ~rtadmin/RTafni/src
   ./getBuildInstallGDCM.sh
   ```

as that user.  This will retrieve and install the GrassRoots DICOM
package, which is used to parse and retrieve information which
cannot be obtained by the pydicom libraries (for example, information
in the vendor's private DICOM fields).

The container's 'rtadmin' user should also run:

   ```bash
   @update.afni.binaries -package linux_openmp_64 -bindir /home/rtadmin/RTafni/bin/AFNI/
   ```

to retrieve and install the latest AFNI binaries.

