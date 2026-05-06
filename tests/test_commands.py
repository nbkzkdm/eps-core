import json
from argparse import Namespace
from pathlib import Path

import pytest

from eps.commands.entry import handle as entry_handle
from eps.commands.view import handle as view_handle
from eps.commands.modify import handle as modify_handle
from eps.commands.delete import handle as delete_handle
from eps.commands.exe import handle as exe_handle
from eps.commands.save import handle as save_handle
from eps.commands.load import handle as load_handle
from eps.commands.settings import handle_view, handle_modify


def store_path(tmp_path):
    return tmp_path / ".eps" / "store.json"


def read_store(tmp_path):
    return json.loads(store_path(tmp_path).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_entry_register_with_name(tmp_path):
    args = Namespace(
        command=["echo", "$1"],
        name="sample01",
        force=False,
    )

    entry_handle(args)

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo $1"}
    ]


def test_entry_register_without_name(tmp_path):
    args = Namespace(
        command=["echo", "hello"],
        name=None,
        force=False,
    )

    entry_handle(args)

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "echo-hello", "command": "echo hello"}
    ]


def test_entry_duplicate_without_force_is_error(tmp_path, capsys):
    entry_handle(Namespace(command=["echo", "hello"], name="sample01", force=False))
    entry_handle(Namespace(command=["echo", "hello2"], name="sample01", force=False))

    captured = capsys.readouterr()

    assert "[ERROR] Entry 'sample01' already exists." in captured.out
    assert "Use --force to overwrite." in captured.out

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo hello"}
    ]


def test_entry_duplicate_with_force_overwrites(tmp_path):
    entry_handle(Namespace(command=["echo", "hello"], name="sample01", force=False))
    entry_handle(Namespace(command=["echo", "hello2"], name="sample01", force=True))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo hello2"}
    ]


def test_view_single_entry(tmp_path, capsys):
    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    view_handle(Namespace(name="sample01", all=False))

    captured = capsys.readouterr()

    assert "[ENTRY] sample01" in captured.out
    assert "[COMMAND] echo $1" in captured.out


def test_view_all_entries(tmp_path, capsys):
    entry_handle(Namespace(command=["echo", "a"], name="a", force=False))
    entry_handle(Namespace(command=["echo", "b"], name="b", force=False))

    view_handle(Namespace(name=None, all=True))

    captured = capsys.readouterr()

    assert "[ENTRY] a" in captured.out
    assert "[COMMAND] echo a" in captured.out
    assert "[ENTRY] b" in captured.out
    assert "[COMMAND] echo b" in captured.out


def test_modify_entry(tmp_path, monkeypatch):
    entry_handle(Namespace(command=["echo", "old"], name="sample01", force=False))

    monkeypatch.setattr("builtins.input", lambda prompt: "echo new")

    modify_handle(Namespace(name="sample01"))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo new"}
    ]


def test_delete_yes(tmp_path, monkeypatch):
    entry_handle(Namespace(command=["echo", "hello"], name="sample01", force=False))

    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    delete_handle(Namespace(name="sample01"))

    store = read_store(tmp_path)
    assert store["entries"] == []


def test_delete_no(tmp_path, monkeypatch):
    entry_handle(Namespace(command=["echo", "hello"], name="sample01", force=False))

    monkeypatch.setattr("builtins.input", lambda prompt: "no")

    delete_handle(Namespace(name="sample01"))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo hello"}
    ]


def test_exe_with_direct_argument(tmp_path, capsys):
    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    exe_handle(Namespace(name="sample01", values=["goodmorning"]))

    captured = capsys.readouterr()

    assert "[COMMAND] echo goodmorning" in captured.out
    assert "[RESULT]" in captured.out
    assert "goodmorning" in captured.out


def test_exe_with_interactive_argument(tmp_path, monkeypatch, capsys):
    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    monkeypatch.setattr("builtins.input", lambda prompt: "goodmorning")

    exe_handle(Namespace(name="sample01", values=[]))

    captured = capsys.readouterr()

    assert "[COMMAND] echo goodmorning" in captured.out
    assert "goodmorning" in captured.out


def test_exe_too_many_arguments(tmp_path, capsys):
    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    exe_handle(Namespace(name="sample01", values=["a", "b"]))

    captured = capsys.readouterr()

    assert "[ERROR] Too many arguments." in captured.out
    assert "Required: 1" in captured.out
    assert "Given: 2" in captured.out


def test_save_default_path(tmp_path):
    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    save_handle(Namespace())

    saved_file = tmp_path / "eps-settings.json"

    assert saved_file.exists()

    data = json.loads(saved_file.read_text(encoding="utf-8"))
    assert data == {
        "entries": [
            {"name": "sample01", "command": "echo $1"}
        ]
    }


def test_save_existing_file_no_does_not_overwrite(tmp_path, monkeypatch):
    target = tmp_path / "eps-settings.json"
    target.write_text("old", encoding="utf-8")

    entry_handle(Namespace(command=["echo", "$1"], name="sample01", force=False))

    monkeypatch.setattr("builtins.input", lambda prompt: "no")

    save_handle(Namespace())

    assert target.read_text(encoding="utf-8") == "old"


def test_settings_view(tmp_path, capsys):
    handle_view(Namespace())

    captured = capsys.readouterr()

    assert "save.file.path: ~" in captured.out
    assert "save.file.name: eps-settings.json" in captured.out


def test_settings_modify_save_file_path(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "/tmp")

    handle_modify(Namespace(key="save.file.path"))

    store = read_store(tmp_path)
    assert store["settings"]["save"]["file"]["path"] == "/tmp"


def test_load_entries(tmp_path):
    load_file = tmp_path / "load.json"
    load_file.write_text(
        json.dumps({
            "entries": [
                {"name": "sample01", "command": "echo $1"}
            ]
        }),
        encoding="utf-8"
    )

    load_handle(Namespace(file=str(load_file), skip=False, force=False))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo $1"}
    ]


def test_load_duplicate_default_renames(tmp_path):
    entry_handle(Namespace(command=["echo", "old"], name="sample01", force=False))

    load_file = tmp_path / "load.json"
    load_file.write_text(
        json.dumps({
            "entries": [
                {"name": "sample01", "command": "echo new"}
            ]
        }),
        encoding="utf-8"
    )

    load_handle(Namespace(file=str(load_file), skip=False, force=False))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo old"},
        {"name": "sample012", "command": "echo new"},
    ]


def test_load_duplicate_skip(tmp_path):
    entry_handle(Namespace(command=["echo", "old"], name="sample01", force=False))

    load_file = tmp_path / "load.json"
    load_file.write_text(
        json.dumps({
            "entries": [
                {"name": "sample01", "command": "echo new"}
            ]
        }),
        encoding="utf-8"
    )

    load_handle(Namespace(file=str(load_file), skip=True, force=False))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo old"}
    ]


def test_load_duplicate_force(tmp_path):
    entry_handle(Namespace(command=["echo", "old"], name="sample01", force=False))

    load_file = tmp_path / "load.json"
    load_file.write_text(
        json.dumps({
            "entries": [
                {"name": "sample01", "command": "echo new"}
            ]
        }),
        encoding="utf-8"
    )

    load_handle(Namespace(file=str(load_file), skip=False, force=True))

    store = read_store(tmp_path)
    assert store["entries"] == [
        {"name": "sample01", "command": "echo new"}
    ]


def test_load_invalid_format(tmp_path, capsys):
    load_file = tmp_path / "invalid.json"
    load_file.write_text(
        json.dumps({
            "items": []
        }),
        encoding="utf-8"
    )

    load_handle(Namespace(file=str(load_file), skip=False, force=False))

    captured = capsys.readouterr()

    assert "[ERROR]" in captured.out
