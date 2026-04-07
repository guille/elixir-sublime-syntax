from pathlib import Path
from typing import cast

import sublime
import sublime_plugin

from .utils import reverse_find_root_folder


class MixTestSwitchToCodeOrTestCommand(sublime_plugin.TextCommand):
    def description(self):
        return "Finds the corresponding source file of the test and vice versa if possible."

    def is_enabled(self) -> bool:
        syntax = self.view.syntax()
        return syntax is not None and syntax.scope == "source.elixir"

    def run(self, _edit):
        window = self.view.window()
        if window is None:
            return

        abs_path = self.view.file_name()
        if abs_path is None:
            return

        file_path = Path(abs_path)
        parts = file_path.name.rsplit("_test.exs", 1)
        is_test = parts[1:] == [""]
        search_names = (
            [parts[0] + ext for ext in (".ex", ".exs")]
            if is_test
            else [file_path.stem + "_test.exs"]
        )

        ignored_folders = [".elixir_ls", "_build", "deps"] + cast(
            "list[str]",
            sublime.load_settings("Preferences.sublime-settings").get(
                "folder_exclude_patterns"
            ),
        )

        subpaths = [
            p
            for folder in (window.folders() or [reverse_find_root_folder(file_path)])
            if folder
            for p in Path(folder).iterdir()
            if p.is_file() or p.name not in ignored_folders
        ]

        counterpart_paths = [
            (subpath, p)
            for subpath in subpaths
            for p in (subpath.rglob("*.ex*") if subpath.is_dir() else [subpath])
            if p.name in search_names
        ]

        if len(counterpart_paths) > 1:

            def on_select(i: int):
                if i >= 0:
                    window.open_file(str(counterpart_paths[i][1]))

            file_path_items = [
                sublime.QuickPanelItem(
                    trigger=str(path.relative_to(folder)),
                    details="Folder: %s" % folder,
                    kind=sublime.KIND_NAVIGATION,
                )
                for folder, path in counterpart_paths
            ]

            window.show_quick_panel(file_path_items, on_select)
        elif counterpart_paths:
            window.open_file(str(counterpart_paths[0][1]))
        else:
            test_or_code = ["test", "code"][is_test]
            window.status_message(
                "ElixirSyntax error: could not find the counterpart %s file."
                % test_or_code
            )
