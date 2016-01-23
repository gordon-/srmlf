import locale

import pytest

from localemock import LocaleMock


def test_init():
    lm = LocaleMock('POSIX')
    assert isinstance(lm, LocaleMock)
    assert lm.new_locale == 'POSIX'


def test_init_with_categories():
    lm = LocaleMock('POSIX', [locale.LC_NUMERIC, locale.LC_TIME])
    assert locale.LC_NUMERIC in lm.categories
    assert locale.LC_NUMERIC in lm.old_locales


def test_inexistant_locale():
    with pytest.raises(locale.Error):
        LocaleMock('inexistant_locale')


def test_wrong_param():
    with pytest.raises(TypeError):
        LocaleMock(1)
    with pytest.raises(TypeError):
        LocaleMock({})
    with pytest.raises(TypeError):
        LocaleMock('test', 'test')


def test_tuple_locale():
    old_locale = locale.getlocale()
    lm = LocaleMock(('POSIX', None))
    assert lm.old_locales[locale.LC_CTYPE] == old_locale
    lm = LocaleMock(('fr_FR', 'utf-8'))
    assert lm.old_locales[locale.LC_CTYPE] == old_locale


def test_new_locale():
    lm = LocaleMock('fr_FR')
    lm.__enter__()
    assert locale.getlocale()[0] == 'fr_FR'


def test_new_locale_with_category():
    old_locale = locale.getlocale(locale.LC_MONETARY)
    lm = LocaleMock('fr_FR', [locale.LC_TIME])
    lm.__enter__()
    assert locale.getlocale(locale.LC_TIME)[0] == 'fr_FR'
    assert locale.getlocale(locale.LC_MONETARY) == old_locale


def test_new_locale_with_multiple_categories():
    old_locale = locale.getlocale(locale.LC_MESSAGES)
    lm = LocaleMock('fr_FR', [locale.LC_TIME, locale.LC_MONETARY])
    lm.__enter__()
    assert locale.getlocale(locale.LC_TIME)[0] == 'fr_FR'
    assert locale.getlocale(locale.LC_MONETARY)[0] == 'fr_FR'
    assert locale.getlocale(locale.LC_MESSAGES) == old_locale


def test_old_locale():
    old_locale = locale.getlocale()
    lm = LocaleMock('POSIX')
    lm.__enter__()
    assert lm.old_locales[locale.LC_CTYPE] == old_locale


def test_old_locale_with_category():
    old_locale = locale.getlocale(locale.LC_TIME)
    lm = LocaleMock('POSIX', [locale.LC_TIME])
    lm.__enter__()
    lm.__exit__()
    assert locale.getlocale(locale.LC_TIME) == old_locale


def test_exit():
    old_locale = locale.getlocale()
    lm = LocaleMock('POSIX')
    lm.__enter__()
    lm.__exit__()
    assert locale.getlocale() == old_locale


def test_with_statement():
    old_locale = locale.getlocale()
    with LocaleMock('fr_FR'):
        assert locale.getlocale()[0] == 'fr_FR'
    assert locale.getlocale() == old_locale
