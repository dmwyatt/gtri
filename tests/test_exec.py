from unittest.mock import patch, MagicMock
import subprocess

import pytest

from gtri.exec import find_executable, run_subprocess, exec_replace


class TestFindExecutable:
    def test_found(self):
        with patch("shutil.which", return_value="/usr/bin/git"):
            assert find_executable("git") == "/usr/bin/git"

    def test_not_found(self):
        with patch("shutil.which", return_value=None):
            assert find_executable("nonexistent") is None


class TestRunSubprocess:
    def test_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = run_subprocess(["git", "gtr", "new", "feat"])
            mock_run.assert_called_once_with(["git", "gtr", "new", "feat"], check=True)
            assert result.returncode == 0

    def test_raises_on_failure(self):
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")):
            with pytest.raises(subprocess.CalledProcessError):
                run_subprocess(["git", "gtr", "new", "feat"])


class TestExecReplace:
    def test_calls_execvp(self):
        with patch("os.execvp") as mock_execvp:
            exec_replace(["git", "gtr", "ai", "main"])
            mock_execvp.assert_called_once_with("git", ["git", "gtr", "ai", "main"])

    def test_passes_correct_argv(self):
        with patch("os.execvp") as mock_execvp:
            exec_replace(["git", "gtr", "rm", "feat", "--delete-branch"])
            mock_execvp.assert_called_once_with(
                "git", ["git", "gtr", "rm", "feat", "--delete-branch"]
            )
