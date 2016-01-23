import locale


class LocaleMock():

    def __init__(self, new_locale, categories=None):
        self.old_locales = {}
        self.new_locale = new_locale
        self.categories = categories if categories is not None else\
            [locale.LC_CTYPE]
        for category in self.categories:
            self.old_locales[category] = locale.getlocale(category)

        # testing given locale
        old_locales = locale.getlocale(locale.LC_CTYPE)
        locale.setlocale(locale.LC_CTYPE, self.new_locale)
        locale.setlocale(locale.LC_CTYPE, old_locales)

    def __enter__(self):
        for category in self.categories:
            locale.setlocale(category, self.new_locale)

    def __exit__(self, *args, **kwargs):
        for category in self.categories:
            locale.setlocale(category, self.old_locales[category])
