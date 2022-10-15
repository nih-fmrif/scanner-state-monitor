
## Resources for file monitors using Python.

Initially, a more direct interface to [inotify](https://man7.org/linux/man-pages/man7/inotify.7.html) was being considered, such as [PyInotify](https://github.com/dsoprea/PyInotify) or [intoify_simple](https://github.com/chrisjbillington/inotify_simple). However, because inotify inherently depends on Linux kernel APIs, these did not seem to work in macOS when installed to a Conda environment, even though these packages were successfully downloaded and installed.  This [issue](https://github.com/benoitc/gunicorn/issues/1540) seems to bear this out.

A more platform agnostic API for real-time file monitoring seems to be [watchdog](https://github.com/gorakhargosh/watchdog).  According to its documentation, it uses inotify on Linux, FSEevents and kqueue on macOS, with support for Windows and CIFS volumes.  This will be utilized and tested in initial implementations.  'watchdog' also seems to have current and consistent development than 'inotify'.  Here's a [simple example](https://levelup.gitconnected.com/how-to-monitor-file-system-events-in-python-e8e0ed6ec2c) of how to set up and use 'watchdog'.

One particularly useful example is [this one](https://gist.github.com/mivade/f4cb26c282d421a62e8b9a341c7c65f6) that shows how 'watchdog' can be called from an 'asyncio' event loop manager.

