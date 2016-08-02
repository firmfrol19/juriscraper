import idaho_civil


class Site(idaho_civil.Site):
    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.url = 'http://www.isc.idaho.gov/appeals-court/isc_criminal'
        self.court_id = self.__module__