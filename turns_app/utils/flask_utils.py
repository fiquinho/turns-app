# pycharm_flask_debug_patch.py
import os
import subprocess
from dataclasses import dataclass

# noinspection PyProtectedMember
import werkzeug._reloader
# noinspection PyProtectedMember
from werkzeug._reloader import _log, _get_args_for_reloading

from turns_app.turns import MongoTurnsManager
from turns_app.utils.dataclass_utils import BaseDataclass


@dataclass
class ApiState(BaseDataclass):
    db_manager: MongoTurnsManager


def restart_with_reloader_patch(self) -> int:
    """Spawn a new Python interpreter with the same arguments as the
    current one, but running the reloader thread.
    """
    while True:
        _log("info", f" * Restarting with {self.name}")
        args = _get_args_for_reloading()
        new_environ = os.environ.copy()
        new_environ["WERKZEUG_RUN_MAIN"] = "true"

        # WORK-AROUND FIX #
        args = [f'""{a}""' if " " in a else a for a in args]
        # WORK-AROUND FIX #

        exit_code = subprocess.call(args, env=new_environ, close_fds=False)

        if exit_code != 3:
            return exit_code


# noinspection PyProtectedMember
def update_werkzeug_reloader():
    werkzeug._reloader.ReloaderLoop.restart_with_reloader = restart_with_reloader_patch
