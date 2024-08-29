import io
from unittest import TestCase, mock

from install_process.install import InstallProcess, InstallStep, DisplayStdout, InstallSteps, Config


class TestDisplayStdout(TestCase):
    def setUp(self) -> None:
        print("")

    def test_msg(self) -> None:
        display = DisplayStdout()
        display.msg('test msg')

        display.context.index = 1
        display.msg('test msg')

        display.context.index = 2
        display.msg('test msg')
        display.context.index = 0

        output = io.StringIO()
        display.stdout = output
        display.msg('test msg')
        self.assertEqual(f'{display.TABS}test msg\x1b[0m\n', output.getvalue())

        display.context.index = 1
        output = io.StringIO()
        display.stdout = output
        display.msg('test msg')
        self.assertEqual(f'{display.TABS}{display.TABS}test msg\x1b[0m\n', output.getvalue())

        display.context.index = 2
        output = io.StringIO()
        display.stdout = output
        display.msg('test msg')
        self.assertEqual(f'{display.TABS}{display.TABS}{display.TABS}test msg\x1b[0m\n', output.getvalue())

    def test_get_input(self) -> None:
        display = DisplayStdout()

        with mock.patch('builtins.input', return_value='user_name'):
            self.assertEqual('user_name', display.get_input("Enter your name: "))

    def test_get_password(self) -> None:
        display = DisplayStdout()

        with mock.patch('getpass.getpass', return_value='1234supersafe'):
            self.assertEqual('1234supersafe', display.get_password("Enter your password: "))

    def test_msg_long_string(self) -> None:
        display = DisplayStdout()
        display.msg(f'test {"very " * 40}long msg')
        display.msg(f'test very l{"o" * 180}ng msg')

        output = io.StringIO()
        display.stdout = output
        display.msg(f'test {"very " * 40}long msg')
        display.msg(f'test very l{"o" * 180}ng msg')
        for line in output.getvalue().split('\n'):
            self.assertLessEqual(len(line), display.terminal_width + 30, f'line to long:\n{line}')

    def test_warn(self) -> None:
        display = DisplayStdout()
        display.warn('test warn')

        display.context.index = 1
        display.warn('test warn')

        display.context.index = 2
        display.warn('test warn')

    def test_warn_long_string(self) -> None:
        display = DisplayStdout()
        display.warn(f'test {"very " * 40}long msg')
        display.warn(f'test very l{"o" * 180}ng msg')

        output = io.StringIO()
        display.stdout = output
        display.warn(f'test {"very " * 40}long msg')
        display.warn(f'test very l{"o" * 180}ng msg')
        for line in output.getvalue().split('\n'):
            self.assertLessEqual(len(line), display.terminal_width + 30, f'line to long:\n{line}')

    def test_error(self) -> None:
        display = DisplayStdout()
        display.error('test error')

        display.context.index = 1
        display.error('test error')

        display.context.index = 2
        display.error('test error')

    def test_error_long_string(self) -> None:
        display = DisplayStdout()
        display.error(f'test {"very " * 40}long msg')
        display.error(f'test very l{"o" * 180}ng msg')

        output = io.StringIO()
        display.stdout = output
        display.error(f'test {"very " * 40}long msg')
        display.error(f'test very l{"o" * 180}ng msg')
        for line in output.getvalue().split('\n'):
            self.assertLessEqual(len(line), display.terminal_width + 30, f'line to long:\n{line}')



    def test_step_new(self) -> None:
        display = DisplayStdout()
        display.step_new('test step_new')

        display.context.index = 1
        display.context.step_count = 1
        display.step_new('test step_new')

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        display.step_new('test step_new')
        display.context.index = 0
        display.context.current_step = 0
        display.context.step_count = 0

        output = io.StringIO()
        display.stdout = output
        display.step_new('test step_new')
        self.assertEqual('\x1b[1m[0/0] test step_new\x1b[0m\n', output.getvalue())

        display.context.index = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_new('test step_new')
        self.assertEqual(f'{display.TABS}\x1b[1m[0/1] test step_new\x1b[0m\n', output.getvalue())

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_new('test step_new')
        self.assertEqual(f'{display.TABS}{display.TABS}\x1b[1m[1/1] test step_new\x1b[0m\n', output.getvalue())

    def test_step_end(self) -> None:
        display = DisplayStdout()
        display.step_end('test step_end')

        display.context.index = 1
        display.context.step_count = 1
        display.step_end('test step_end')

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        display.step_end('test step_end')
        display.context.index = 0
        display.context.current_step = 0
        display.context.step_count = 0

        output = io.StringIO()
        display.stdout = output
        display.step_end('test step_end')
        self.assertEqual('┗━> \x1b[92mtest step_end\x1b[0m\n', output.getvalue())

        display.context.index = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_end('test step_end')
        self.assertEqual(f'{display.TABS}┗━> \x1b[92mtest step_end\x1b[0m\n', output.getvalue())

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_end('test step_end')
        self.assertEqual(f'{display.TABS}{display.TABS}┗━> \x1b[92mtest step_end\x1b[0m\n', output.getvalue())

    def test_step_skip(self) -> None:
        display = DisplayStdout()
        display.step_skip('test step_skip')

        display.context.index = 1
        display.context.step_count = 1
        display.step_skip('test step_skip')

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        display.step_skip('test step_skip')
        display.context.index = 0
        display.context.current_step = 0
        display.context.step_count = 0

        output = io.StringIO()
        display.stdout = output
        display.step_skip('test step_skip')
        self.assertEqual('┗━> \x1b[33mtest step_skip\x1b[0m\n', output.getvalue())

        display.context.index = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_skip('test step_skip')
        self.assertEqual(f'{display.TABS}┗━> \x1b[33mtest step_skip\x1b[0m\n', output.getvalue())

        display.context.index = 2
        display.context.current_step = 1
        display.context.step_count = 1
        output = io.StringIO()
        display.stdout = output
        display.step_skip('test step_skip')
        self.assertEqual(f'{display.TABS}{display.TABS}┗━> \x1b[33mtest step_skip\x1b[0m\n', output.getvalue())

    def test_shell_cmd(self) -> None:
        display = DisplayStdout()
        display.shell_cmd('test shell_cmd')

        output = io.StringIO()
        display.stdout = output
        display.shell_cmd('test shell_cmd')
        self.assertEqual(f'{display.TABS}$> test shell_cmd\x1b[0m\n', output.getvalue())

    def test_shell_output(self) -> None:
        display = DisplayStdout()
        display.shell_output('test shell_output')

        output = io.StringIO()
        display.stdout = output
        display.shell_output('test shell_output')
        self.assertEqual(f'{display.TABS}\x1b[3m\x1b[90mtest shell_output\x1b[0m\n', output.getvalue())

    def test_begin_all(self) -> None:
        display = DisplayStdout()
        display.begin_all('test begin_all')

        output = io.StringIO()
        display.stdout = output
        display.begin_all('test begin_all')
        self.assertEqual(f'\x1b[4m\x1b[1mtest begin_all\x1b[0m\n', output.getvalue())


class TestInstallStep(TestCase):
    class InstallStepSimple(InstallStep):
        _install_flag = False
        _uninstall_flag = False

        def install(self) -> None:
            """Install step"""
            self.__class__._install_flag = True

        def uninstall(self) -> None:
            """Uninstall step"""
            self.__class__._uninstall_flag = True

    class InstallStepConditionFalse(InstallStep):
        _install_flag = False
        _uninstall_flag = False

        def install_condition(self) -> bool:
            """Skip install"""
            return False

        def install(self) -> None:
            """Should skip install"""
            self.__class__._install_flag = True

        def uninstall_condition(self) -> bool:
            """Skip uninstall"""
            return False

        def uninstall(self) -> None:
            """Should skip uninstall"""
            self.__class__._uninstall_flag = True

    def setUp(self) -> None:
        print("")

    def tearDown(self) -> None:
        self.InstallStepSimple._install_flag = False
        self.InstallStepSimple._uninstall_flag = False

        self.InstallStepConditionFalse._install_flag = False
        self.InstallStepConditionFalse._uninstall_flag = False

    def test_install(self) -> None:
        simple_step = self.InstallStepSimple()
        simple_step.install()
        self.assertTrue(simple_step._install_flag)

    def test_uninstall(self) -> None:
        simple_step = self.InstallStepSimple()
        simple_step.uninstall()
        self.assertTrue(simple_step._uninstall_flag)

    def test_install_condition(self) -> None:
        false_condition_step = self.InstallStepConditionFalse()
        false_condition_step._process_install()
        self.assertFalse(false_condition_step._install_flag)

    def test_uninstall_condition(self) -> None:
        false_condition_step = self.InstallStepConditionFalse()
        false_condition_step._process_uninstall()
        self.assertFalse(false_condition_step._uninstall_flag)

    def test_process_install(self) -> None:
        simple_step = self.InstallStepSimple()
        simple_step._process_install()
        self.assertTrue(simple_step._install_flag)

    def test_process_uninstall(self) -> None:
        simple_step = self.InstallStepSimple()
        simple_step._process_uninstall()
        self.assertTrue(simple_step._uninstall_flag)

    def test__get_child(self) -> None:
        simple_step = self.InstallStepSimple()
        print(simple_step._get_child())


class TestInstallSteps(TestCase):
    class InstallStepsSimple(InstallSteps):
        """A simple collection of install steps."""
        steps = [
            TestInstallStep.InstallStepSimple(),
            TestInstallStep.InstallStepConditionFalse(),
        ]

    def setUp(self) -> None:
        print("")

    def tearDown(self) -> None:
        TestInstallStep.InstallStepSimple._install_flag = False
        TestInstallStep.InstallStepSimple._uninstall_flag = False

        TestInstallStep.InstallStepConditionFalse._install_flag = False
        TestInstallStep.InstallStepConditionFalse._uninstall_flag = False

    def test_process_install(self) -> None:
        install_steps = self.InstallStepsSimple()
        install_steps._process_install()
        self.assertTrue(TestInstallStep.InstallStepSimple._install_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._install_flag)

    def test_process_uninstall(self) -> None:
        install_steps = self.InstallStepsSimple()
        install_steps._process_uninstall()
        self.assertTrue(TestInstallStep.InstallStepSimple._uninstall_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._uninstall_flag)

    def test_total_steps(self) -> None:
        install_steps = self.InstallStepsSimple()
        self.assertEqual(3, install_steps.total_steps())

    def test__get_child(self) -> None:
        install_steps = self.InstallStepsSimple()
        print(install_steps._get_child())


class TestTopInstall(TestCase):
    class InstallProcessEmpty(InstallProcess):
        """EMPTY TOP INSTALL TEST"""

    class InstallProcessSimple(InstallProcess):
        """SIMPLE TOP INSTALL TEST"""
        steps = [
            TestInstallSteps.InstallStepsSimple(),
        ]

    def setUp(self) -> None:
        print("")

    def tearDown(self) -> None:
        TestInstallStep.InstallStepSimple._install_flag = False
        TestInstallStep.InstallStepSimple._uninstall_flag = False

        TestInstallStep.InstallStepConditionFalse._install_flag = False
        TestInstallStep.InstallStepConditionFalse._uninstall_flag = False

        Config.only_show_names = False

    def test_process_install_empty(self) -> None:
        top_install = TestTopInstall.InstallProcessEmpty()
        top_install.install()

    def test_process_uninstall_empty(self) -> None:
        top_install = TestTopInstall.InstallProcessEmpty()
        top_install.uninstall()

    def test_process_install_simple(self) -> None:
        top_install = TestTopInstall.InstallProcessSimple()
        top_install.install()
        self.assertTrue(TestInstallStep.InstallStepSimple._install_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._install_flag)

    def test_process_uninstall_simple(self) -> None:
        top_install = TestTopInstall.InstallProcessSimple()
        top_install.uninstall()
        self.assertTrue(TestInstallStep.InstallStepSimple._uninstall_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._uninstall_flag)

    def test_process_install_specific(self) -> None:
        top_install = TestTopInstall.InstallProcessSimple(
            'TestInstallSteps.InstallStepsSimple.TestInstallStep.InstallStepSimple')
        top_install.install()
        self.assertTrue(TestInstallStep.InstallStepSimple._install_flag)

        with self.assertRaises(ValueError):
            TestTopInstall.InstallProcessSimple('Non-Existent-Step-Name')

    def test_process_uninstall_specific(self) -> None:
        top_install = TestTopInstall.InstallProcessSimple(
            'TestInstallSteps.InstallStepsSimple.TestInstallStep.InstallStepSimple')
        top_install.uninstall()
        self.assertTrue(TestInstallStep.InstallStepSimple._uninstall_flag)

        with self.assertRaises(ValueError):
            TestTopInstall.InstallProcessSimple('Non-Existent-Step-Name')

    def test_process_install_name_only(self) -> None:
        Config.only_show_names = True
        top_install = TestTopInstall.InstallProcessSimple()
        top_install.install()
        self.assertFalse(TestInstallStep.InstallStepSimple._install_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._install_flag)

    def test_process_uninstall_name_only(self) -> None:
        Config.only_show_names = True
        top_install = TestTopInstall.InstallProcessSimple()
        top_install.uninstall()
        self.assertFalse(TestInstallStep.InstallStepSimple._uninstall_flag)
        self.assertFalse(TestInstallStep.InstallStepConditionFalse._uninstall_flag)
