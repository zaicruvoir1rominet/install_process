from __future__ import annotations

import abc
import argparse
import concurrent.futures
import copy
import ctypes
import getpass
import inspect
import io
import shutil
import subprocess
import sys
import textwrap
from typing import TextIO


class Config:

    verbose = False
    """Display the output of shell commands."""

    only_show_names = False
    """Do not install/uninstall, only show step names."""

    root_required = False
    """Check if root/admin privileges are granted before install/uninstall."""

    process_name = ""
    """Name of the step/steps to launch. If empty string, launch all steps."""


class Context:
    """Current installation execution context."""

    def __init__(self):
        self.current_step = 0
        """Number of the current install/uninstall step being run."""

        self.step_count = 0
        """Total number of install/uninstall steps."""

        self.index = 0
        """Level of imbrication of the install/uninstall step being run."""


class Display(abc.ABC):
    """Defines how install steps are displayed."""

    @abc.abstractmethod
    def print(self, msg: str) -> None:
        """Display an install message"""

    @abc.abstractmethod
    def msg(self, msg: str) -> None:
        """Display an installation message inside an install-step."""

    @abc.abstractmethod
    def warn(self, msg: str) -> None:
        """Display an installation warning message inside an install-step."""

    @abc.abstractmethod
    def error(self, msg: str) -> None:
        """Display an installation error message inside an install-step."""

    @abc.abstractmethod
    def get_input(self, _prompt: str) -> str:
        """Just like the ``input`` function from Python, but using this display"""

    @abc.abstractmethod
    def get_password(self, _prompt: str) -> str:
        """Just like the ``getpass.getpass`` function from Python, but using this display"""

    @abc.abstractmethod
    def step_new(self, msg: str) -> None:
        """Setup display for a new install step."""

    @abc.abstractmethod
    def step_end(self, msg: str) -> None:
        """End display for an install-step."""

    @abc.abstractmethod
    def step_new_parallel(self, msg: str) -> None:
        """Setup display for a new install-step."""

    @abc.abstractmethod
    def step_end_parallel(self, msg: str) -> None:
        """End display for an install-step."""

    @abc.abstractmethod
    def step_skip(self, msg: str) -> None:
        """End display for an install-step, when step is skipped."""

    @abc.abstractmethod
    def shell_cmd(self, cmd: str) -> None:
        """Setup display for a new shell command inside an install-step."""

    @abc.abstractmethod
    def shell_output(self, output: str) -> None:
        """Display for a new shell command inside an install-step."""

    @abc.abstractmethod
    def begin_all(self, msg: str) -> None:
        """Setup display for the entire install-process."""


class DisplayStdout(Display):
    """Default stdout display."""

    TABS = "┃   "
    GREEN = "\033[92m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREY = "\033[90m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"

    terminal_width = shutil.get_terminal_size()[0]

    def __init__(self, stdout: TextIO | None = None, context: Context | None = None) -> None:
        self.stdout = stdout or sys.stdout
        self.context = context or Context()

    def _format_msg(self, msg: str, index: int, first_indent: str = "", indents: str = "", color: str = "") -> str:
        msg_line_max_length = self.terminal_width - len(self.TABS * index) - len(indents) - 1
        if not msg_line_max_length:
            return msg  # give up!

        lines = textwrap.wrap(msg, msg_line_max_length)
        if lines:
            if first_indent:
                lines[0] = f"{self.TABS * index}{first_indent}{color}{lines[0]}{self.ENDC}"
            else:
                lines[0] = f"{self.TABS * index}{indents}{color}{lines[0]}{self.ENDC}"

            if len(lines) > 1:
                for line_num, line in enumerate(lines[1:], start=1):
                    lines[line_num] = f"{self.TABS * index}{indents}{color}{line}{self.ENDC}"

        return "\n".join(lines)

    def msg(self, msg: str) -> None:
        print(self._format_msg(msg, self.context.index + 1), file=self.stdout)

    def warn(self, msg: str) -> None:
        previous_frame = inspect.currentframe().f_back
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
        print(self._format_msg(f"{filename}:{line_number}: WARNING",
                               self.context.index,
                               color=self.BOLD + self.YELLOW,
                               first_indent=f"{self.BOLD}{self.YELLOW}┣━> ",
                               indents=self.TABS),
              file=self.stdout)
        print(self._format_msg(msg,
                               self.context.index,
                               color=self.YELLOW,
                               indents="┃     "),
              file=self.stdout)

    def error(self, msg: str) -> None:
        previous_frame = inspect.currentframe().f_back
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
        print(self._format_msg(f"{filename}:{line_number}: ERROR",
                               self.context.index,
                               color=self.BOLD + self.RED,
                               first_indent=f"{self.BOLD}{self.RED}┣━> ",
                               indents=self.TABS),
              file=self.stdout)
        print(self._format_msg(msg,
                               self.context.index,
                               color=self.RED,
                               indents="┃     "),
              file=self.stdout)

    def get_input(self, _prompt: str) -> str:
        return input(self._format_msg(_prompt, self.context.index + 1,
                                      color=self.YELLOW))

    def get_password(self, _prompt: str) -> str:
        return getpass.getpass(self._format_msg(_prompt, self.context.index + 1,
                               color=self.YELLOW))

    def print(self, msg: str) -> None:
        print(msg, file=self.stdout, end="")

    def step_new(self, msg: str) -> None:
        print(self._format_msg(f"[{self.context.current_step}/{self.context.step_count}] {msg}",
                               self.context.index,
                               color=self.BOLD),
              file=self.stdout)

    def step_end(self, msg: str) -> None:
        print(self._format_msg(msg,
                               self.context.index,
                               color=self.GREEN,
                               first_indent="┗━> "),
              file=self.stdout)

    def step_new_parallel(self, msg: str) -> None:
        print(self._format_msg(msg,
                               self.context.index - 1,
                               color=self.BOLD,
                               first_indent=f"{self.BOLD}┣━> "),
              file=self.stdout)

    def step_end_parallel(self, msg: str) -> None:
        pass

    def step_skip(self, msg: str) -> None:
        print(self._format_msg(msg,
                               self.context.index,
                               color=self.YELLOW,
                               first_indent="┗━> "),
              file=self.stdout)

    def shell_cmd(self, cmd: str) -> None:
        print(self._format_msg(f"$> {cmd}",
                               self.context.index + 1),
              file=self.stdout)

    def shell_output(self, output: str) -> None:
        print(self._format_msg(output,
                               self.context.index + 1,
                               color=self.ITALIC + self.GREY,),
              file=self.stdout)

    def begin_all(self, msg: str) -> None:
        print(self._format_msg(msg,
                               0,
                               color=self.UNDERLINE + self.BOLD, ),
              file=self.stdout)


class InstallStep(abc.ABC):
    r"""An installation step, giving details on how to install a simple element of your
    entire installation process.
    Here you should also describe how to uninstall this element, if applicable.

    Implement the `install` and `uninstall` methods to do so.
    Docstrings of the `install` and `uninstall` methods will be displayed during the install process.

    You may want to overwrite `install_condition` and `uninstall_condition`.

    Examples:

        A couple of install steps to setup a Python dev env
        (just an example, I would recommend using hatch or any dedicated tools):

        >>> import pathlib
        ... import shutil
        ...
        ... class InstallPythonDependencies(InstallStep):
        ...     def install(self) -> None:
        ...         '''Install dependencies'''
        ...         self.shell("pip install pytest sphinx ruff")
        ...     def uninstall(self) -> None:
        ...         '''Remove dependencies'''
        ...         self.shell("pip uninstall pytest sphinx ruff")
        ...
        ... class SetupPythonDirLayout(InstallStep):
        ...     MY_PROJECT_DIR = pathlib.Path("whatever")
        ...     def install(self) -> None:
        ...         '''Install dependencies'''
        ...         (self.MY_PROJECT_DIR / 'docs').mkdir(parents=True, exist_ok=True)
        ...         (self.MY_PROJECT_DIR / 'tests').mkdir(parents=True, exist_ok=True)
        ...         with open(self.MY_PROJECT_DIR / ".gitignore", "w", encoding="utf-8") as gitignore:
        ...             gitignore.write("\n".join(["__pycache__/", "*.py[cod]", "*$py.class"])
        ...     def uninstall(self) -> None:
        ...         '''Remove dependencies'''
        ...         shutil.rmtree(self.MY_PROJECT_DIR, ignore_errors=True)
    """

    def __init__(self) -> None:
        self._display = DisplayStdout()
        self._father: InstallStep | None = None
        self._context = Context()

    @abc.abstractmethod
    def install(self) -> None:
        """Describe (briefly) what you are installing [here]."""
        pass

    @abc.abstractmethod
    def uninstall(self) -> None:
        """Describe (briefly) what you are installing [here]."""
        pass

    def install_condition(self) -> bool:
        """Overwrite method if you want to skip installation under certain conditions,
        and explain [here] why install should be skipped, if applicable."""
        return True

    def uninstall_condition(self) -> bool:
        """Overwrite method if you want to skip uninstallation under certain conditions,
        and explain [here] why uninstall should be skipped, if applicable."""
        return True

    def total_steps(self) -> int:
        """Number of steps in this install-step(s)."""
        return 1

    def name(self) -> str:
        """Install step name"""
        try:
            father_name = self.father.name()
        except AttributeError:
            return f"{self.__class__.__qualname__}"

        if father_name:
            return f"{father_name}.{self.__class__.__qualname__}"
        return f"{self.__class__.__qualname__}"

    def shell(self, cmd: str, check_error: bool = True, timeout: float = None) -> str:
        """Executes a shell command and returns its output.

        Args:
            cmd: shell cmd to execute
            check_error: if True, check if the shell cmd fails (and raises and Exception if it does fail)
            timeout: raises and Exception if shell cmd still runs after [timeout] seconds

        Returns:
            shell cmd output
        """
        if Config.verbose:
            self.display.shell_cmd(cmd)

        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
        )
        output = result.stdout.strip()

        if output and Config.verbose:
            self.display.shell_output(output)

        if check_error:
            try:
                result.check_returncode()
            except subprocess.CalledProcessError:
                if not Config.verbose:
                    self.display.shell_output(output)
                raise

        return output

    @property
    def display(self) -> Display:
        return self._display

    @display.setter
    def display(self, display: Display) -> None:
        self._display = display

    @property
    def father(self) -> InstallStep:
        return self._father

    @father.setter
    def father(self, father: InstallStep) -> None:
        self._father = father

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context
        self._display.context = context

    def _process_install(self) -> None:
        """Do not overwrite method when defining a new install-step.

        Notes:
            Handles display & config for installation
        """
        if Config.only_show_names:
            self.display.step_new(f"{self.install.__doc__}    {self.name()}")
            return

        self.display.step_new(self.install.__doc__)

        if not self.install_condition():
            self.display.step_skip(self.install_condition.__doc__)
            return

        self.install()
        self.display.step_end("done.")

    def _process_uninstall(self) -> None:
        """Do not overwrite method when defining a new install-step.

        Notes:
            Handles display & config for uninstallation
        """
        if Config.only_show_names:
            self.display.step_new(f"{self.uninstall.__doc__}    {self.name()}")
            return

        self.display.step_new(self.uninstall.__doc__)

        if not self.uninstall_condition():
            self.display.step_skip(self.uninstall_condition.__doc__)
            return

        self.uninstall()
        self.display.step_end("done.")

    def _get_child(self) -> list[tuple[str, InstallStep]]:

        return [(self.name(), self)]

    def __or__(self, other: InstallStep) -> _ParallelInstallSteps:
        parallel_step = _ParallelInstallSteps()
        parallel_step._steps = [self, other]
        return parallel_step


class InstallSteps(InstallStep):
    """A collection of installation steps.

    Define installation steps using the ``steps`` class attribute.
    Docstrings of the install-steps class will be displayed during the install-process.

    You may want to overwrite `install_condition` and `uninstall_condition`.

    Examples:

        >>> # Define some install-steps
        ... class InstallPythonDependencies(InstallStep):
        ...     # ...
        ... class SetupPythonDirLayout(InstallStep):
        ...     # ...
        ...
        ... # Define our collection of install-steps
        ... class SetupPythonEnv(InstallSteps):
        ...     '''Python Env'''
        ...     steps = [
        ...         InstallPythonDependencies(),
        ...         SetupPythonDirLayout(),
        ...     ]
    """

    steps: list[InstallStep] = None

    def __init__(self) -> None:
        self._steps = self.steps if self.steps else []
        for step in self._steps:
            step.father = self
        super().__init__()

    def install(self) -> None:
        """Do not overwrite method when defining install-steps,
        use the ``step`` class attribute instead.

        Notes:
            Handles steps install
        """
        self.context.index += 1
        for step in self._steps:
            self.context.current_step += 1
            step._process_install()
        self.context.index -= 1

    def uninstall(self) -> None:
        """Do not overwrite method when defining install-steps,
        use the ``step`` class attribute instead.

        Notes:
            Handles steps uninstall
        """
        self.context.index += 1
        for step in reversed(self._steps):
            self.context.current_step += 1
            step._process_uninstall()
        self.context.index -= 1

    def total_steps(self) -> int:
        return sum(step.total_steps() for step in self._steps) + 1

    @property
    def display(self) -> Display:
        return self._display

    @display.setter
    def display(self, display: Display) -> None:
        self._display = display
        for step in self._steps:
            step.display = display

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context
        for step in self._steps:
            step.context = context

    def _process_install(self) -> None:
        if Config.only_show_names:
            self.display.step_new(f"Install # {self.__doc__}    {self.name()}")
            self.install()
            return

        self.display.step_new(f"Install # {self.__doc__}")

        if not self.install_condition():
            self.display.step_skip(self.install_condition.__doc__)
            self.context.current_step += self.total_steps()
            return

        self.install()
        self.display.step_end("done.")

    def _process_uninstall(self) -> None:
        if Config.only_show_names:
            self.display.step_new(f"Uninstall # {self.__doc__}    {self.name()}")
            self.uninstall()
            return

        self.display.step_new(f"Uninstall # {self.__doc__}")

        if not self.uninstall_condition():
            self.display.step_skip(self.uninstall_condition.__doc__)
            self.context.current_step += self.total_steps()
            return

        self.uninstall()
        self.display.step_end("done.")

    def _get_child(self) -> list[tuple[str, InstallStep]]:
        child: list[tuple[str, InstallStep]] = [(self.name(), self)]
        for step in self._steps:
            child.extend(step._get_child())
        return child


class _ParallelInstallSteps(InstallSteps):
    def install(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_steps: list[tuple[concurrent.futures.Future, InstallStep]] = []
            previous_step_count = 0
            for step in self._steps:
                self.context.current_step += previous_step_count
                step.display = DisplayStdout(io.StringIO())
                step.context = copy.copy(self.context)
                previous_step_count = step.total_steps()
                future_steps.append((executor.submit(step._process_install), step))
            for future, step in future_steps:
                future.result()
                self.display.print(step.display.stdout.getvalue())
                step.display = DisplayStdout()

    def uninstall(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_steps: list[tuple[concurrent.futures.Future, InstallStep]] = []
            previous_step_count = 0
            for step in reversed(self._steps):
                self.context.current_step += previous_step_count
                step.display = DisplayStdout(io.StringIO())
                step.context = copy.copy(self.context)
                previous_step_count = step.total_steps()
                future_steps.append((executor.submit(step._process_uninstall), step))
            for future, step in future_steps:
                future.result()
                self.display.print(step.display.stdout.getvalue())
                step.display = DisplayStdout()

    def total_steps(self) -> int:
        return sum(step.total_steps() for step in self._steps)

    def _process_install(self) -> None:
        self.display.step_new_parallel(" | ".join(step.__class__.__qualname__ for step in self._steps))
        self.install()

    def _process_uninstall(self) -> None:
        self.display.step_new_parallel(" | ".join(step.__class__.__qualname__ for step in self._steps))
        self.uninstall()

    @property
    def father(self) -> InstallStep:
        return self._steps[0].father

    @father.setter
    def father(self, father: InstallStep) -> None:
        for step in self._steps:
            step.father = father

    def __or__(self, other: InstallStep) -> _ParallelInstallSteps:
        if isinstance(other, _ParallelInstallSteps):
            self._steps.extend(other._steps)
        else:
            self._steps.append(other)
        return self


class InstallProcess(InstallSteps):
    """The required collection of installation steps.

    Define installation steps using the ``steps`` class attribute.
    Docstring of the install-process class will be displayed during the installation process.

    You may want to overwrite `prologue` and `epilogue`.

    Examples:

        >>> # Define some install steps
        ... class InstallPythonDependencies(InstallStep):
        ...     # ...
        ... class SetupPythonDirLayout(InstallStep):
        ...     # ...
        ...
        ... # Define our top install
        ... class SetupPythonEnv(InstallProcess):
        ...     '''Python Env'''
        ...     steps = [
        ...         InstallPythonDependencies(),
        ...         SetupPythonDirLayout(),
        ...     ]
        ...
        ... # Make the file executable
        ... if __name__ == '__main__':
        ...     setup_install(SetupPythonEnv)
    """

    def __init__(self, install_step_name: str = "") -> None:
        super().__init__()
        self._isntall_step_name = install_step_name
        self._steps_dict = {child_name: child_step for child_name, child_step in self._get_child()}
        if self._isntall_step_name and self._isntall_step_name not in self._steps_dict:
            raise ValueError(f"Test step {self._isntall_step_name} does not exist in {self.__class__.__qualname__}")

        self.context = Context()
        self.display = DisplayStdout(context=self.context)

    def install(self) -> None:
        self.display.begin_all(self.__class__.__doc__)
        self._check_root()
        self.prologue()

        if self._isntall_step_name:
            self.context.current_step = 1
            self.context.index += 1
            self.context.step_count = self._steps_dict[self._isntall_step_name].total_steps()
            self._steps_dict[self._isntall_step_name]._process_install()
            self.context.index -= 1
        else:
            self.context.current_step = 0
            self.context.step_count = self.total_steps() - 1
            super().install()

        self.display.step_end("done.")
        self.epilogue()

    def uninstall(self) -> None:
        self.display.begin_all(self.__class__.__doc__)
        self._check_root()
        self.prologue()

        if self._isntall_step_name:
            self.context.current_step = 1
            self.context.index += 1
            self.context.step_count = self._steps_dict[self._isntall_step_name].total_steps()
            self._steps_dict[self._isntall_step_name]._process_uninstall()
            self.context.index -= 1
        else:
            self.context.current_step = 0
            self.context.step_count = self.total_steps() - 1
            super().uninstall()

        self.display.step_end("done.")
        self.epilogue()

    def prologue(self) -> None:
        """Any kind of operation to execute before install/uninstall
        (display summary message, setup things, etc.)"""

    def epilogue(self) -> None:
        """Any kind of operation to execute after install/uninstall
        (display recap message, setup things, etc.)"""

    def name(self) -> str:
        return ""

    def _check_root(self) -> None:
        if not Config.root_required:
            return

        if not "root" == getpass.getuser() or not ctypes.windll.shell32.IsUserAnAdmin():
            raise ValueError(f"Install process {self.__class__.__qualname__} must be "
                             "launched as root / admin (sudo python -m ...)")

    def _get_child(self) -> list[tuple[str, InstallStep]]:
        child: list[tuple[str, InstallStep]] = []
        for step in self._steps:
            child.extend(step._get_child())
        return child


def setup_install(your_install_process: type[InstallProcess],
                  prologue: InstallSteps = None,
                  epilogue: InstallSteps = None) -> None:
    """Command line to set up your installation process.

    Args:
        - your_install_process: your installation process
        - prologue: install steps to add before top_install ones
        - epilogue: install steps to add after top_install ones
    """
    args_parser = argparse.ArgumentParser(description=f'Installation Process for {your_install_process.__qualname__}')
    args_parser.add_argument('-i', '--install_type', help='Installation type',
                             choices=['install', 'uninstall', 'reinstall'],
                             default='install', required=False)
    args_parser.add_argument('-v', '--verbose', help='If set, output all install messages',
                             default=False, action="store_true", required=False)
    args_parser.add_argument('-n', '--only_show_names',
                             help="If set, only shows install step names, but doesn't install or uninstall anything",
                             default=False, action="store_true", required=False)
    args_parser.add_argument('-t', '--step_to_launch',
                             help="Name of the InstallStep (or InstallSteps) to launch. "
                                  "If not set, all steps are launched",
                             default='', required=False)
    args = args_parser.parse_args()

    if args.verbose:
        Config.verbose = True
    if args.only_show_names:
        Config.only_show_names = True

    install = your_install_process(args.step_to_launch)

    if prologue:
        install._steps = [prologue] + install._steps
    if epilogue:
        install._steps = install._steps + [epilogue]

    if args.install_type == "install":
        install.install()
    elif args.install_type == "uninstall":
        install.uninstall()
    else:
        install.uninstall()
        install.install()
