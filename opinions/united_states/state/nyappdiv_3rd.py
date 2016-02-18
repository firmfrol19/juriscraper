# Scraper for New York Appellate Divisions 3rd Dept.
# CourtID: nyappdiv_3rd
# Court Short Name: NY
# History:
#   2014-07-04: Created by Andrei Chelaru
#   2014-07-05: Reviewed by mlr
#   2014-12-15: Updated to fix regex and insanity errors.
#   2016-02-17: Updated by arderyp, regex was breaking due to new page section.

from datetime import date
from dateutil.relativedelta import relativedelta, TH
from juriscraper.OpinionSite import OpinionSite


class Site(OpinionSite):
    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.court_id = self.__module__
        # Last thursday, this court publishes weekly
        self.crawl_date = date.today() + relativedelta(weekday=TH(-1))
        self.url = 'http://decisions.courts.state.ny.us/ad3/CalendarPages/nc{month_nr}{day_nr}{year}.htm'.format(
            month_nr=self.crawl_date.strftime("%m"),
            day_nr=self.crawl_date.strftime("%d"),
            year=self.crawl_date.year
        )
        self.LINK_PATH = "//td[2]//a[contains(./@href, 'Decisions')]"
        self.LINK_TEXT_PATH = '%s/text()' % self.LINK_PATH
        self.LINK_HREF_PATH = '%s/@href' % self.LINK_PATH

    def _get_case_names(self):
        case_names = []
        for link_text in self.html.xpath(self.LINK_TEXT_PATH):
            text = link_text.strip()
            if text:
                case_names.append(text.split(None, 1)[1])
        return case_names

    def _get_download_urls(self):
        return list(self.html.xpath(self.LINK_HREF_PATH))

    def _get_case_dates(self):
        return [self.crawl_date] * len(self.html.xpath(self.LINK_HREF_PATH))

    def _get_precedential_statuses(self):
        return ['Published'] * len(self.case_names)

    def _get_docket_numbers(self):
        docket_numbers = []
        for link_text in self.html.xpath(self.LINK_TEXT_PATH):
            text = link_text.strip()
            if text:
                docket_numbers.append(text.split()[0])
        return docket_numbers