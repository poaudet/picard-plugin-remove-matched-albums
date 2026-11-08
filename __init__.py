"""Remove Matched Albums"""
#
# Copyright (C) 2026 Bob Swift
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.

# This plugin is based on the Picard 2 plugin "Remove Perfect Albums" by
# ichneumon and hrglgrmpf.  See original code at
# https://github.com/metabrainz/picard-plugins/blob/2.0/plugins/remove_perfect_albums/remove_perfect_albums.py
import traceback
from PyQt6 import QtWidgets

from picard.plugin3.api import (
    Album,
    BaseAction,
    OptionsPage,
    PluginApi,
    t_,
)


USER_GUIDE_URL = 'https://picard-plugins-user-guides.readthedocs.io/en/latest/remove_matched_albums/user_guide.html'

OPTION = "only_remove_saved"
LOG = "Remove Matched Albums:"

_api = None  # set in enable()

def _get_only_saved(api):
    try:
        value = api.plugin_config[OPTION]
    except Exception:
        api.logger.error(
            f"{LOG} could not read option:\n{traceback.format_exc()}"
        )
        return False
    # config backends can hand booleans back as the strings "true"/"false"
    return value is True or str(value).lower() == "true"


def _set_only_saved(api, value):
    try:
        api.plugin_config[OPTION] = bool(value)
    except Exception:
        api.logger.error(
            f"{LOG} could not save option:\n{traceback.format_exc()}"
        )

class RemoveCompleteOptionsPage(OptionsPage):
    NAME = "remove_complete_albums"
    TITLE = "Remove Complete Albums"
    PARENT = "plugins"

    def __init__(self, *args, **kwargs):
        # Picard's calling convention for option pages is unclear: find the
        # Qt parent by type and take the api object from enable().
        parent = next(
            (a for a in (*args, *kwargs.values())
             if isinstance(a, QtWidgets.QWidget)),
            None,
        )
        super().__init__(parent)
        self.api = _api
        if _api:
            _api.logger.info(
                f"{LOG} options page created, "
                f"args={[type(a).__name__ for a in args]}, "
                f"kwargs={list(kwargs)}"
            )
        layout = QtWidgets.QVBoxLayout(self)
        self.save_box = QtWidgets.QCheckBox(
            "Only remove albums that have no unsaved files"
        )
        layout.addWidget(self.save_box)
        layout.addStretch()
    def load(self):
        self.save_box.setChecked(_get_only_saved(self.api))

    def save(self):
        _set_only_saved(self.api, self.save_box.isChecked())


class RemoveMatchedAlbums(BaseAction):
    TITLE = t_("ui.action.remove_albums.title", "Remove matched albums")

    def __init__(self, api=None):
        super().__init__()
        self.api = api or _api

    def callback(self, objs):
        only_saved = _get_only_saved(self.api)
        removed = False

        for album in list(set(self.api.tagger.albums.values())):
            if not isinstance(album, Album):
                continue
            if not (album.loaded and album.is_complete()):
                continue
            if only_saved and album.get_num_unsaved_files() > 0:
                continue
            self.api.tagger.remove_album(album)
            removed = True

        if not removed:
            QtWidgets.QMessageBox.warning(
                self.api.tagger.window,
                self.api.tr("ui.dialog.no_albums.title", "No Albums"),
                # new key, so an old translation of the original text isn't shown
                self.api.tr(
                    "ui.dialog.nothing_removed.text",
                    "No albums were removed with the current option settings.",
                ),
                QtWidgets.QMessageBox.StandardButton.Ok,
                QtWidgets.QMessageBox.StandardButton.Ok,
            )

def enable(api: PluginApi):
    """Called when plugin is enabled."""
    global _api
    _api = api
    api.logger.info(f"{LOG} enable() called")
    try:
        api.plugin_config.register_option(OPTION, True)
    except Exception:
        api.logger.error(
            f"{LOG} register_option failed:\n{traceback.format_exc()}"
        )
    api.register_options_page(RemoveCompleteOptionsPage)
    api.logger.info(f"{LOG} options page registered")
    api.register_tools_menu_action(RemoveMatchedAlbums)
    api.logger.info(f"{LOG} tools menu action registered")
