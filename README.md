
# Docker image for the FMRIF's Real-Time AFNI Framework

This reposiotry will hold a Docker container build configuration, in
addition to program files to support FMRIF's real-time AFNI framework.

The command to run this container is:

   ```bash
   docker run --name test-RTafni2 -p 138:138/udp -p 139:139 -p 445:445 -p 445:445/udp -v /data0/:/data0 -it dockerAcctName/containerName:version
   ```

This will start the container with all of the ports needed for Samba
opened and mapped.

The first time the container is run, the Samba password for the meduser
account must be set, with the command:

   ```bash
   smbpasswd meduser
   ```

and after this, the volume shared by the container (/data0) should be
accessible from the console via Samba.

