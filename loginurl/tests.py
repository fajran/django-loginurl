import unittest
from datetime import datetime, timedelta

from mock import Mock, patch, patch_object

from django.contrib.auth.models import User
from django.utils.http import int_to_base36, base36_to_int
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseGone
from django.conf import settings
from django.core import management

from loginurl.models import Key
from loginurl import utils, backends, views

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        Key.objects.all().delete()
        User.objects.all().delete()
        self.user = User.objects.create_user('test', 'test@example.com',
                                             'password')

class CreateKeyTestCase(BaseTestCase):
    def testDefault(self):
        data = utils.create(self.user)

        self.assertEqual(data.usage_left, 1)
        self.assertEqual(data.expires, None)
        self.assertEqual(data.next, None)

        uid_b36, key = data.key.split('-')
        self.assertEqual(int_to_base36(self.user.id), uid_b36)

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(data, datadb)

    def testTenTimes(self):
        data = utils.create(self.user, usage_left=10)
        self.assertEqual(data.usage_left, 10)

    def testOneWeek(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = utils.create(self.user, expires=oneweek)
        self.assertEqual(data.expires, oneweek)

    def testNextPage(self):
        next = '/next/page/'
        data = utils.create(self.user, next=next)
        self.assertEqual(data.next, next)

class CleanUpTestCase(BaseTestCase):
    def testPositive(self):
        data = utils.create(self.user, usage_left=1)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 1)

    def testZero(self):
        data = utils.create(self.user, usage_left=0)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 0)

    def testNegative(self):
        data = utils.create(self.user, usage_left=-1)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 0)

    def testValid(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = utils.create(self.user, usage_left=1, expires=oneweek)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 1)
        
    def testExpired(self):
        oneweekago = datetime.now() - timedelta(days=7)
        data = utils.create(self.user, usage_left=1, expires=oneweekago)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 0)
     
    def testAlwaysValid(self):
        data = utils.create(self.user, usage_left=None, expires=None)
        self.assertEqual(len(Key.objects.all()), 1)

        utils.cleanup()
        self.assertEqual(len(Key.objects.all()), 1)

class ModelCheckValidTestCase(BaseTestCase):
    def testPositive(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=1, expires=oneweek)
        self.assertTrue(data.is_valid())

    def testZero(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=0, expires=oneweek)
        self.assertFalse(data.is_valid())

    def testNegative(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=-1, expires=oneweek)
        self.assertFalse(data.is_valid())

    def testValid(self):
        oneweek = datetime.now() + timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=1, expires=oneweek)
        self.assertTrue(data.is_valid())
        
    def testExpired(self):
        oneweekago = datetime.now() - timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=1, expires=oneweekago)
        self.assertFalse(data.is_valid())
     
    def testAlwaysValid(self):
        data = Key.objects.create(user=self.user, usage_left=None, expires=None)
        self.assertTrue(data.is_valid())
        
    def testBothInvalid(self):
        oneweekago = datetime.now() - timedelta(days=7)
        data = Key.objects.create(user=self.user, usage_left=-1, expires=oneweekago)
        self.assertFalse(data.is_valid())
     
class ModelUpdateUsageTestCase(BaseTestCase):
    def testDefault(self):
        data = Key.objects.create(user=self.user)
        self.assertEqual(data.usage_left, 1)

        data.update_usage()

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)
        
    def testNone(self):
        data = Key.objects.create(user=self.user, usage_left=None)
        self.assertEqual(data.usage_left, None)

        data.update_usage()

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, None)

    def testZero(self):
        data = Key.objects.create(user=self.user, usage_left=0)
        self.assertEqual(data.usage_left, 0)

        data.update_usage()

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)

    def testPositive(self):
        data = Key.objects.create(user=self.user, usage_left=100)
        self.assertEqual(data.usage_left, 100)

        data.update_usage()

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 99)

    def testNegative(self):
        data = Key.objects.create(user=self.user, usage_left=-100)
        self.assertEqual(data.usage_left, -100)

        data.update_usage()

        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, -100)

class BackendTestCase(BaseTestCase):
    def setUp(self):
        self.backend = backends.LoginUrlBackend()
        BaseTestCase.setUp(self)

    def testValid(self):
        data = utils.create(self.user)

        res = self.backend.authenticate(data.key)
        self.assertEqual(res, self.user)

    def testInvalidKey(self):
        data = utils.create(self.user)
        invalid_key = '%s-invalid' % data.key

        res = self.backend.authenticate(invalid_key)
        self.assertEqual(res, None)

    def testInvalid(self):
        data = utils.create(self.user, usage_left=0)

        res = self.backend.authenticate(data.key)
        self.assertEqual(res, None)

    def testGetUser(self):
        data = utils.create(self.user, usage_left=0)

        user = self.backend.get_user(self.user.id)
        self.assertEqual(user, self.user)

class ViewCleanUpTestCase(unittest.TestCase):
    def testCleanUp(self):
        mock = Mock()

        @patch_object(utils, 'cleanup', mock)
        def test():
            return views.cleanup(None)

        res = test()

        self.assertTrue(mock.called)
        self.assertTrue(isinstance(res, HttpResponse))
        self.assertTrue(res.status_code, 200)

class ViewLoginTestCae(BaseTestCase):
    def testDefault(self):
        auth = Mock()
        auth.authenticate.return_value = self.user

        req = Mock()
        req.GET.get.return_value = None

        data = utils.create(self.user)
        self.assertEqual(data.usage_left, 1)

        @patch_object(views, 'auth', auth)
        def test(request, key):
            return views.login(request, key)

        res = test(req, data.key)

        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], settings.LOGIN_REDIRECT_URL)
            
        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)

    def testInvalidKey(self):
        auth = Mock()
        auth.authenticate.return_value = None

        req = Mock()
        req.GET.get.return_value = None

        @patch_object(views, 'auth', auth)
        def test(request):
            return views.login(request, 'invalid-key')

        res = test(req)

        next = '%s?next=%s' % (settings.LOGIN_URL, 
                               settings.LOGIN_REDIRECT_URL)
        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], next)

    def testNextFromDB(self):
        auth = Mock()
        auth.authenticate.return_value = self.user

        req = Mock()
        req.GET.get.return_value = None

        data = utils.create(self.user, next='/next/page/')
        self.assertEqual(data.usage_left, 1)

        @patch_object(views, 'auth', auth)
        def test(request, key):
            return views.login(request, key)

        res = test(req, data.key)

        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], '/next/page/')
            
        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)

    def testNextFromQueryString(self):
        auth = Mock()
        auth.authenticate.return_value = self.user

        req = Mock()
        req.GET.get.return_value = '/next/page/'

        data = utils.create(self.user)
        self.assertEqual(data.usage_left, 1)

        @patch_object(views, 'auth', auth)
        def test(request, key):
            return views.login(request, key)

        res = test(req, data.key)

        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], '/next/page/')
            
        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)

    def testNext(self):
        auth = Mock()
        auth.authenticate.return_value = self.user

        req = Mock()
        req.GET.get.return_value = '/next/query-string/'

        data = utils.create(self.user, next='/next/database/')
        self.assertEqual(data.usage_left, 1)

        @patch_object(views, 'auth', auth)
        def test(request, key):
            return views.login(request, key)

        res = test(req, data.key)

        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], '/next/database/')
            
        datadb = Key.objects.get(key=data.key)
        self.assertEqual(datadb.usage_left, 0)

    def testInvalidKeyNext(self):
        auth = Mock()
        auth.authenticate.return_value = None

        req = Mock()
        req.GET.get.return_value = '/next/query-string/'

        @patch_object(views, 'auth', auth)
        def test(request):
            return views.login(request, 'invalid-key')

        res = test(req)

        next = '%s?next=%s' % (settings.LOGIN_URL, '/next/query-string/')
        self.assertTrue(isinstance(res, HttpResponseRedirect))
        self.assertEqual(res['Location'], next)

class CommandTestCase(unittest.TestCase):
    def testCall(self):
        from loginurl.management.commands import loginurl_cleanup

        mock = Mock()
        
        @patch_object(utils, 'cleanup', mock)
        def test():
            management.call_command('loginurl_cleanup')

        test()

        self.assertTrue(mock.called)

