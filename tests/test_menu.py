"""Behavioral tests for reusable terminal menus."""

from dataclasses import FrozenInstanceError
from unittest.mock import Mock

import pytest

from safeserve_tui.menu import Menu, MenuBuilder, MenuEntry, MenuHeader


@pytest.mark.parametrize("value", [None, 1, True])
def test_header_rejects_non_strings(value):
    with pytest.raises(TypeError):
        MenuHeader(value)


@pytest.mark.parametrize("value", ["", " ", "\t\n"])
def test_header_rejects_blank_text(value):
    with pytest.raises(ValueError):
        MenuHeader(value)


@pytest.mark.parametrize("value", [None, 1, True])
def test_entry_rejects_non_string_labels(value):
    with pytest.raises(TypeError):
        MenuEntry(value, Mock())


@pytest.mark.parametrize("value", ["", " ", "\t\n"])
def test_entry_rejects_blank_labels(value):
    with pytest.raises(ValueError):
        MenuEntry(value, Mock())


@pytest.mark.parametrize("action", [None, 1, "action"])
def test_entry_requires_a_callable(action):
    with pytest.raises(TypeError):
        MenuEntry("Exit", action)


def test_menu_renders_header_and_zero_based_choices_without_normalizing_text():
    menu = MenuBuilder(MenuHeader(" Main menu ")).with_entry(
        "List dishes", Mock()
    ).with_entry("Exit", Mock()).build()

    assert menu.render() == " Main menu \n0) List dishes\n1) Exit\n"


@pytest.mark.parametrize("index", [0, 1])
def test_selection_runs_only_the_selected_action(index):
    actions = [Mock(), Mock()]
    menu = MenuBuilder(MenuHeader("Main")).with_entry(
        "List", actions[0]
    ).with_entry("Exit", actions[1]).build()

    menu.select(index)

    actions[index].assert_called_once_with()
    actions[1 - index].assert_not_called()


@pytest.mark.parametrize("index", [-1, 2, 100])
def test_out_of_range_selection_runs_no_action(index):
    action = Mock()
    menu = MenuBuilder(MenuHeader("Main")).with_entry("Exit", action).build()

    with pytest.raises(ValueError):
        menu.select(index)

    action.assert_not_called()


@pytest.mark.parametrize("index", [None, "0", 0.0, True, False])
def test_selection_requires_an_integer_not_a_boolean(index):
    action = Mock()
    menu = MenuBuilder(MenuHeader("Main")).with_entry("Exit", action).build()

    with pytest.raises(TypeError):
        menu.select(index)

    action.assert_not_called()


def test_action_failures_propagate_to_the_application():
    def fail():
        raise RuntimeError("Service unavailable")

    menu = MenuBuilder(MenuHeader("Main")).with_entry("List", fail).build()

    with pytest.raises(RuntimeError, match="Service unavailable"):
        menu.select(0)


@pytest.mark.parametrize("header", [None, "Main"])
def test_menu_and_builder_require_a_validated_header(header):
    with pytest.raises(TypeError):
        Menu(header, (MenuEntry("Exit", Mock()),))
    with pytest.raises(TypeError):
        MenuBuilder(header)


def test_empty_menu_is_rejected_through_both_construction_paths():
    header = MenuHeader("Main")
    with pytest.raises(ValueError):
        Menu(header, ())
    with pytest.raises(ValueError):
        MenuBuilder(header).build()


@pytest.mark.parametrize("entries", [None, "Exit", 1])
def test_menu_rejects_invalid_entry_collections(entries):
    with pytest.raises(TypeError):
        Menu(MenuHeader("Main"), entries)


def test_menu_validates_every_entry():
    with pytest.raises(TypeError):
        Menu(MenuHeader("Main"), (MenuEntry("Exit", Mock()), "invalid"))


def test_menu_copies_the_supplied_list():
    entries = [MenuEntry("Exit", Mock())]
    menu = Menu(MenuHeader("Main"), entries)

    entries.clear()

    assert menu.render() == "Main\n0) Exit\n"
    assert isinstance(menu.entries, tuple)


def test_builder_changes_do_not_change_previously_built_menus():
    builder = MenuBuilder(MenuHeader("Main")).with_entry("List", Mock())
    first = builder.build()
    builder.with_entry("Exit", Mock())
    second = builder.build()

    assert first.render() == "Main\n0) List\n"
    assert second.render() == "Main\n0) List\n1) Exit\n"
    assert builder.build().render() == second.render()


def test_rejected_entry_does_not_change_the_builder():
    builder = MenuBuilder(MenuHeader("Main")).with_entry("Exit", Mock())

    with pytest.raises(ValueError):
        builder.with_entry(" ", Mock())

    assert builder.build().render() == "Main\n0) Exit\n"


@pytest.mark.parametrize("target, field, value", [
    (MenuHeader("Main"), "text", "Changed"),
    (MenuEntry("Exit", Mock()), "label", "Changed"),
    (MenuEntry("Exit", Mock()), "action", Mock()),
    (Menu(MenuHeader("Main"), (MenuEntry("Exit", Mock()),)), "entries", ()),
    (
        Menu(MenuHeader("Main"), (MenuEntry("Exit", Mock()),)),
        "header",
        MenuHeader("Other"),
    ),
])
def test_built_menu_configuration_is_immutable(target, field, value):
    with pytest.raises(FrozenInstanceError):
        setattr(target, field, value)



def test_building_and_rendering_do_not_run_actions_or_write_output(capsys):
    action = Mock()
    menu = MenuBuilder(MenuHeader("Main")).with_entry("Exit", action).build()

    text = menu.render()

    assert text == "Main\n0) Exit\n"
    action.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""
