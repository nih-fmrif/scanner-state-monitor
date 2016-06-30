
# Docker image for the FMRIF's Real-Time AFNI Framework

This reposiotry will hold a Docker container build configuration, in
addition to program files to support FMRIF's real-time AFNI framework.

Initial iterations of building this container had it running Samba to
provide a shared volume to the MRI scanner console.  This capability
has been disabled in the current iteration of the container build due
to the persistence issue of Samba being only available when the container
is running, and any remote volume connection issues that might arise if
the service provision depends on the container running or not.

If running Samba within the container is desired, all the necessary
software and configurations are still included in this repository. To
enable running Samba from within the container, in the Dockerfile, the
comment ('#') marks should be removed from the following lines:

   # ADD smb.conf                  /etc/samba

   # RUN smbpasswd -L -n -a meduser

The lines starting up Samba in the '.startup' script (that is copied to
the container, and is the command that the container starts up with)
should also have their '#' comment marks removed.

Then, the first time the container is run, the Samba password for the
meduser account must be set, with the command:

   ```bash
   smbpasswd meduser
   ```

and after this, the volume shared by the container (/data0) should be
accessible from the MRI's console computer via Windows File Sharing.

The command to run this container with Samba services and accompanyting
ports available is:

   ```bash
   docker run --name rtAFNI -p 138:138/udp -p 139:139 -p 445:445 -p 445:445/udp -p 8111:8111 \
                            -e DISPLAY=unix$DISPLAY -v /data0/:/data0 -v /tmp/.X11-unix/:/tmp/.X11-unix/ \
                            -it dockerAcctName/containerName:version
   ```

Without Samba services (current container configuration), the command
to run this is:

   ```bash
   docker run --name rtAFNI -p 8111:8111 \
                            -e DISPLAY=unix$DISPLAY -v /data0/:/data0 -v /tmp/.X11-unix/:/tmp/.X11-unix/ \
                            -it dockerAcctName/containerName:version
   ```

This will start the container with all of the port chosen for the scanner
console to send messages to, and for the DICOM listener (running in the
container) to observe.

The tip about which variables to pass through to get X11 apps forwarded
through and displaying on host was found at:

   https://blog.jessfraz.com/post/docker-containers-on-the-desktop/

This has pointed the container to the correct X11 DISPLAY to use, but a:

   ```bash
   xhost +
   ```

commnad on the host PC might still be needed to allow X11 connections
from the container to be established.

