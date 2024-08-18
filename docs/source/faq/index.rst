FAQ
===

Frequently asked question about ``install_process``

Can I use an install-step several times ?
-----------------------------------------

Yes you can.

Here is an example of ``Step2`` used several times in an installation process:

.. code-block:: python

    # [...]

    class Step1(InstallStep):
        # ...

    class Step2(InstallStep):
        # ...

    class Step3(InstallStep):
        # ...

    class MyInstallProcess(InstallSteps):
        steps = [
            Step1(),
            Step2(),
            Step2(),
            Step3(),
            Step2(),
        ]

    if __name__ == '__main__':
        setup_install(MyInstallProcess)

----

Is there a way to easily make 2 installation processes which share some steps, for example Windows/Linux install ?
------------------------------------------------------------------------------------------------------------------

You can in a way, by making install-steps groups.

Here is an example of a possible install flow for Linux and Windows:

.. code-block:: python

    # [...]

    class CommonStepsForWindowsAndLinux(InstallSteps):
        # Here are listed the steps for both Linux and Windows

    class SpecificsForWindows(InstallSteps):
        # Here are listed the steps for Windows only

    class SpecificsForLinux(InstallSteps):
        # Here are listed the steps for Linux only

    class WindowsInstallProcess(InstallProcess):
        """INSTALL PROCESS FOR WINDOWS"""
        steps = [
            CommonStepsForWindowsAndLinux(),
            SpecificsForWindows(),
        ]

    class LinuxInstallProcess(InstallProcess):
        """INSTALL PROCESS FOR LINUX"""
        steps = [
            CommonStepsForWindowsAndLinux(),
            SpecificsForLinux(),
        ]


If you want to enable the CLI, you can then make 2 separate files for Linux & Windows:

.. code-block:: python

    # File install_linux.py

    # [...]

    if __name__ == '__main__':
        setup_install(LinuxInstallProcess)


.. code-block:: python

    # File install_windows.py

    # [...]

    if __name__ == '__main__':
        setup_install(WindowsInstallProcess)


And then call which ever installation you like:

.. code-block:: bash

    python -m install_windows
    python -m install_linux

----

Is there a way to trigger specific actions before/after install ?
-----------------------------------------------------------------

You can do so by using overwriting the ``prologue``/``epilogue`` methods of your ``InstallProcess``, or
from the command line by providing steps to the ``prologue``/``epilogue`` parameters of ``setup_install``.

Do note that ``prologue`` will trigger before install, and **before** uninstall ;
and that ``epilogue`` will trigger after install, and **after** uninstall.
