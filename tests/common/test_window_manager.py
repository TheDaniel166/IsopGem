import os
import sys
import pytest

# Ensure local 'src' package is importable
sys.path.append(os.path.join(os.getcwd(), 'src'))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication, QWidget
from shared.ui.window_manager import WindowManager


class TestWindow(QWidget):
    def __init__(self, name='Test', parent=None):
        super().__init__(parent)
        self.setWindowTitle(name)


@pytest.fixture(scope='module')
def app():
    app = QApplication([])
    yield app
    app.quit()


def test_open_and_reuse_single(app):
    wm = WindowManager()
    w1 = wm.open_window('single', TestWindow, allow_multiple=False)
    assert wm.get_window_count() == 1

    # Reopen should return same instance
    w2 = wm.open_window('single', TestWindow, allow_multiple=False)
    assert w1 is w2
    assert wm.get_window_count() == 1

    wm.close_all_windows()
    assert wm.get_window_count() == 0


def test_open_multiple_and_close(app):
    wm = WindowManager()
    w1 = wm.open_window('multi', TestWindow, allow_multiple=True)
    w2 = wm.open_window('multi', TestWindow, allow_multiple=True)
    assert wm.get_window_count() == 2

    # Close first
    id1 = w1.property('window_id')
    assert wm.close_window(id1)
    assert wm.get_window_count() == 1

    # Open another to ensure counters continue
    w3 = wm.open_window('multi', TestWindow, allow_multiple=True)
    assert wm.get_window_count() == 2

    # Close windows by type
    closed = wm.close_windows_of_type('multi')
    assert closed >= 2
    assert wm.get_window_count() == 0


if __name__ == '__main__':
    pytest.main(['-q', os.path.realpath(__file__)])
