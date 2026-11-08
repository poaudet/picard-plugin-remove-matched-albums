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

from PyQt6 import QtWidgets

from picard.plugin3.api import (
    Album,
    BaseAction,
    PluginApi,
    t_,
)


USER_GUIDE_URL = 'https://picard-plugins-user-guides.readthedocs.io/en/latest/remove_matched_albums/user_guide.html'

OPTION = "remove_complete_save_first"
BoolOption("plugins", OPTION, False)

class RemoveCompleteOptionsPage(OptionsPage):
    NAME = "remove_complete_albums"
    TITLE = "Remove Complete Albums"
    PARENT = "plugins"

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.save_box = QtWidgets.QCheckBox(
            "Save complete albums before removing them")
        layout.addWidget(self.save_box)
        layout.addStretch()

    def load(self):
        self.save_box.setChecked(get_config().setting[OPTION])

    def save(self):
        get_config().setting[OPTION] = self.save_box.isChecked()

class RemoveMatchedAlbums(BaseAction):
    TITLE = t_('ui.action.remove_albums.title', "Remove matched albums")

    def callback(self, objs):
        save_first = get_config().setting[OPTION]
        removed = False
        albums = list(set(self.api.tagger.albums.values()))
        for album in albums:
            if not isinstance(album, Album):
                continue

            if album.loaded and album.is_complete():
                if not save_first or album.get_num_unsaved_files() == 0:
                    removed = True
                    self.api.tagger.remove_album(album)

        if not removed:
            QtWidgets.QMessageBox.warning(
                self.api.tagger.window,
                self.api.tr('ui.dialog.no_albums.title', "No Albums"),
                self.api.tr(
                    'ui.dialog.no_albums.text',
                    "There were no completely matched and saved albums found for removal.",
                ),
                QtWidgets.QMessageBox.StandardButton.Ok,
                QtWidgets.QMessageBox.StandardButton.Ok,
            )


def enable(api: PluginApi):
    """Called when plugin is enabled."""
    api.register_options_page(RemoveCompleteOptionsPage)
    api.register_tools_menu_action(RemoveMatchedAlbums)
