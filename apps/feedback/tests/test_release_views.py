import json

from nose import SkipTest
from nose.tools import eq_
from product_details.version_compare import Version
from pyquery import PyQuery as pq

from feedback.models import Opinion
from input import (
    FIREFOX, LATEST_RELEASE, MAX_FEEDBACK_LENGTH, MAX_IDEA_LENGTH,
    OPINION_BROKEN, OPINION_IDEA, OPINION_RATING,
    RATING_CHOICES, RATING_USAGE)
from input.tests import FX_UA, ViewTestCase, enforce_ua
from input.urlresolvers import reverse


class ReleaseTests(ViewTestCase):
    """Test feedback for Firefox release versions."""

    def _get_page(self, ver=None):
        """Request release feedback page."""
        extra = dict(HTTP_USER_AGENT=FX_UA % ver) if ver else {}

        return self.client.get(reverse('feedback', channel='release'), **extra)

    @enforce_ua
    def test_no_ua(self):
        """No UA: redirect."""
        r = self._get_page()
        eq_(r.status_code, 302)
        assert r['Location'].endswith(reverse('feedback.download',
                                              channel='release'))

    @enforce_ua
    def test_beta(self):
        """Beta version on release page: redirect."""
        raise SkipTest
        r = self._get_page('3.6b2')
        self.assertRedirects(r, reverse('feedback', channel='beta'), 302, 302)

    # TODO bug 634324. Reenable this after Firefox 4 release.
    @enforce_ua
    def notest_old_release(self):
        """Post Fx4: Old release: redirect to release download page."""
        r = self._get_page('3.5')
        eq_(r.status_code, 302)
        assert r['Location'].endswith(reverse('feedback.download',
                                              channel='release'))

    # TODO bug 634324. Remove this after Firefox 4 release.
    @enforce_ua
    def test_old_release(self):
        """Pre Fx4: Old release: redirect to beta download page."""
        raise SkipTest
        r = self._get_page('3.5')
        eq_(r.status_code, 302)
        assert r['Location'].endswith(reverse('feedback.download',
                                              channel='beta'))
    # TODO bug 634324. Reenable this after Firefox 4 release.
    @enforce_ua
    def notest_latest_release(self):
        """Post Fx4: Latest release: no redirect."""
        r = self._get_page(LATEST_RELEASE[FIREFOX])
        eq_(r.status_code, 200)

    # TODO bug 634324. Remove this after Firefox 4 release.
    @enforce_ua
    def notest_latest_release(self):
        """Pre Fx4: Firefox 4: no redirect."""
        rel_ver = Version(LATEST_RELEASE[FIREFOX])
        r = self._get_page('4.0' if Version('4.0') > rel_ver else
                           rel_ver._version)
        eq_(r.status_code, 200)

    @enforce_ua
    def test_newer_release(self):
        """Release version newer than current: no redirect."""
        r = self._get_page('20.0')
        eq_(r.status_code, 200)

    @enforce_ua
    def test_nightly(self):
        """Nightly version: redirect."""
        r = self._get_page('20.0b2pre')
        eq_(r.status_code, 302)
        assert r['Location'].endswith(reverse('feedback.download',
                                              channel='beta'))

    def post_feedback(self, data, ajax=False, follow=True):
        """POST to the release feedback page."""
        options = dict(HTTP_USER_AGENT=(FX_UA % '20.0'), follow=follow)
        if ajax:
            options['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

        return self.client.post(reverse('feedback', channel='release'), data,
                                **options)
