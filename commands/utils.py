from pathlib import Path


def reverse_find_root_folder(bottom_path):
    bottom_path = Path(bottom_path)
    parent_path = bottom_path.parent if bottom_path.is_file() else bottom_path

    while True:
        # We have to check for the root mix.exs, ignoring possible sub-app mix files.
        if (parent_path / "mix.exs").exists() and (
            (parent_path / "mix.lock").exists()
            or (parent_path / "_build").exists()
            or parent_path.name != "apps"
            and not (parent_path.parent / "mix.exs").exists()
        ):
            return str(parent_path)

        old_path, parent_path = parent_path, parent_path.parent

        if old_path == parent_path:
            break

    return None
