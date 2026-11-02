import pytest

from evalathan.desk import add_heading, checkout_name, classify, clone_url, prepare


def test_blank_paste_is_refused() -> None:
    with pytest.raises(ValueError, match="Paste"):
        classify("  ")


def test_github_link_is_not_a_folder() -> None:
    kind, url = classify("https://github.com/python/cpython.git")
    assert kind == "github"
    assert checkout_name(url) == "python__cpython"


def test_clone_url_strips_tree_and_blob_paths() -> None:
    assert (
        clone_url("https://github.com/python/cpython/tree/main/Lib")
        == "https://github.com/python/cpython.git"
    )
    assert (
        clone_url("https://github.com/python/cpython/blob/main/README.rst")
        == "https://github.com/python/cpython.git"
    )


def test_local_folder_is_used_as_itself(tmp_path) -> None:
    folder, note = prepare(str(tmp_path))
    assert folder == tmp_path
    assert note == ""


def test_missing_folder_is_refused(tmp_path) -> None:
    with pytest.raises(ValueError, match="not found"):
        prepare(str(tmp_path / "missing"))


def test_logo_sits_at_the_top_right() -> None:
    tk = pytest.importorskip("tkinter")
    from tkinter import ttk

    root = tk.Tk()
    root.withdraw()
    try:
        frame = ttk.Frame(root)
        add_heading(frame, root)
        name, logo = frame.winfo_children()[0].pack_slaves()
        assert name.cget("text") == "HYDRA"
        assert name.pack_info()["side"] == "left"
        assert logo.cget("image")
        assert logo.pack_info()["side"] == "right"
        assert root._hydra_mark.height() == round(56 * 1.12 * 1.16 * 1.11)
    finally:
        root.destroy()
