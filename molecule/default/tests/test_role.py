import pytest
import re


@pytest.mark.parametrize('name', [
    'test_usr1',
    'test_usr2',
    'test_usr6',
])
def test_oh_my_zsh_state(host, name):
    oh_my_zsh = host.file('/home/' + name + '/.oh-my-zsh')
    assert oh_my_zsh.exists
    assert oh_my_zsh.is_directory
    assert oh_my_zsh.user == name
    assert oh_my_zsh.group in [name, 'users']


@pytest.mark.parametrize('name', [
    'test_usr3',
    'test_usr5',
])
def test_oh_my_zsh_is_not_installed_for_excluded_users(host, name):
    oh_my_zsh = host.file('/home/' + name + '/.oh-my-zsh')
    zshrc = host.file('/home/' + name + '/.zshrc')
    assert not oh_my_zsh.exists
    assert not zshrc.exists


@pytest.mark.parametrize('name', [
    'test_usr4',
    'test_usr5',
])
def test_oh_my_zshrc_is_not_installed_for_excluded_users(host, name):
    zshrc = host.file('/home/' + name + '/.zshrc')
    assert not zshrc.exists


@pytest.mark.parametrize('name,theme,plugins,update_mode,update_frequency',
                         [
                             ('test_usr1',
                              'test_theme1',
                              'test_plugin1 test_plugin2',
                              'disabled',
                              '13'),
                             ('test_usr2',
                              'test_theme2',
                              'test_plugin3 test_plugin4',
                              'auto',
                              '31'),
                         ])
def test_oh_my_zsh_config(host, name, theme, plugins,
                          update_mode, update_frequency):
    zshrc = host.file('/home/' + name + '/.zshrc')
    assert zshrc.exists
    assert zshrc.is_file
    assert zshrc.user == name
    assert zshrc.group in [name, 'users']
    assert zshrc.contains(theme)
    assert zshrc.contains(plugins)

    pattern = f"zstyle ':omz:update' mode {update_mode}"
    pattern = r'^' + re.escape(pattern) + r'$'
    assert re.search(pattern, zshrc.content_string, re.MULTILINE), (
        f"{name}: Pattern '{pattern}' not found in {zshrc.content_string}")

    pattern = f"zstyle ':omz:update' frequency {update_frequency}"
    if update_mode == 'disabled':
        pattern = f'# {pattern}'
    pattern = r'^' + re.escape(pattern) + r'$'
    assert re.search(pattern, zshrc.content_string, re.MULTILINE), (
        f"{name}: Pattern '{pattern}' not found in {zshrc.content_string}")


def test_console_setup(host):
    # console-setup is Debian family specific
    if host.file('/etc/debian_version').exists:
        setup = host.file('/etc/default/console-setup')
        assert setup.exists
        assert setup.is_file
        assert setup.user == 'root'
        assert setup.group == 'root'
        assert setup.contains('CHARMAP="UTF-8"')
