import time
from unittest import TestCase

from install_process import InstallStep, InstallSteps, InstallProcess


class Step1(InstallStep):
    def install(self) -> None:
        """Install step 1"""
        self.display.msg("Step 1")
        time.sleep(2)

    def uninstall(self) -> None:
        """Uninstall step 1"""
        self.display.msg("Step 1")
        time.sleep(2)


class Step2(InstallStep):
    def install(self) -> None:
        """Install step 2"""
        time.sleep(1)
        self.display.msg("Step 2")
        time.sleep(1)

    def uninstall(self) -> None:
        """Uninstall step 2"""
        time.sleep(1)
        self.display.msg("Step 2")
        time.sleep(1)


class Step3(InstallStep):
    def install(self) -> None:
        """Install step 3"""
        time.sleep(2)
        self.display.msg("Step 3")

    def uninstall(self) -> None:
        """Uninstall step 3"""
        time.sleep(2)
        self.display.msg("Step 3")


class Step1and2(InstallSteps):
    """Step1 // Step2"""
    steps = [Step1() | Step2()]


class Step1then2(InstallSteps):
    """Step1 then Step2"""
    steps = [Step1(), Step2()]


class ParallelSteps(InstallProcess):
    """Step1 // Step2 // Step3"""
    steps = [Step1() | Step2() | Step3()]


class ParallelCollectionAndSteps(InstallProcess):
    """[Step1 // Step2] // Step3"""
    steps = [Step1and2() | Step3()]


class MixParallelAndNotParallel(InstallProcess):
    """[Step1 then Step2] // Step3"""
    steps = [Step1then2() | Step3()]


class TestParallelInstallSteps(TestCase):
    def setUp(self) -> None:
        print("")

    def test_install_parallel_steps(self) -> None:
        ParallelSteps().install()
        time.sleep(0.1)

    def test_install_parallel_steps_and_collection(self) -> None:
        ParallelCollectionAndSteps().install()
        time.sleep(0.1)

    def test_install_mix_parallel_and_sequential_steps(self) -> None:
        MixParallelAndNotParallel().install()
        time.sleep(0.1)

    def test_uninstall_parallel_steps(self) -> None:
        ParallelSteps().uninstall()
        time.sleep(0.1)

    def test_uninstall_parallel_steps_and_collection(self) -> None:
        ParallelCollectionAndSteps().uninstall()
        time.sleep(0.1)

    def test_uninstall_mix_parallel_and_sequential_steps(self) -> None:
        MixParallelAndNotParallel().uninstall()
        time.sleep(0.1)
