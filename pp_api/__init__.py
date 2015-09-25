# -*- coding: utf-8 -*-

import urllib2
import urllib
import collections
import hashlib

try:
    import json
except ImportError:
    import simplejson as json

DEFAULT_TIMEOUT = 13
REQUEST_ENCODING = 'utf8'


class PricePlanError(Exception):
    __slots__ = ["error"]

    def __init__(self, error_data):
        if 'errors' in error_data:
            self.error = error_data['errors'][0]
        elif type(error_data) is list:
            self.error = error_data[0]
        else:
            self.error = error_data

        Exception.__init__(self, str(self))

    @property
    def code(self):
        print self.error
        return str(self.error['code'])

    @property
    def description(self):
        if 'data' in self.error:
            return str(self.error['data'])
        else:
            return ''

    @property
    def params(self):
        if 'field' in self.error:
            return str(self.error['field'])
        else:
            return ''

    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)


class _PricePlanCore():
    def __init__(self, user, url_base, key=None):
        self.user = user
        self.key = key
        self.url_base = url_base
        self.api_v = 0.1

    def _sortByAlphabet(self, sordet_dict):
        sordet_sorted = sorted(sordet_dict.iteritems(), key=lambda x: x)
        sordet = collections.OrderedDict()
        for i in sordet_sorted:
            sordet[i[0]] = i[1]
        return sordet

    def _get_token(self, key, params):
        p_string = ['%s=%s' % (i, urllib.quote_plus(str(params[i])))
                    for i in params]
        p_string = '&'.join(p_string)
        token = hashlib.md5()
        token.update(p_string + key)
        return token.hexdigest()

    def _get(self, method, timeout=DEFAULT_TIMEOUT, http_method="POST", **kwargs):
        try:
            status, response = self._request(method, timeout=timeout, http_method=http_method, **kwargs)

        except urllib2.HTTPError, e:
            raise PricePlanError({
                'code': e.getcode(),
                'data': "HTTP error",
                'request_params': kwargs,
            })

        if not (200 <= status <= 299):
            raise PricePlanError({
                'code': status,
                'data': "HTTP error",
                'request_params': kwargs,
            })

        data = json.loads(response, strict=False)
        if "errors" in data:
            raise PricePlanError(data["errors"])

        return data


    def _encode(self, s):
        if isinstance(s, unicode):
            s = s.encode(REQUEST_ENCODING)
        return s


    #отправка запроса в PricPlan
    def _request(self, method, timeout=DEFAULT_TIMEOUT,
                 http_method="POST", BODY=None, **kwargs):

        for key, value in kwargs.copy().iteritems():
            if type(value) is dict:
                f_param_count = 0
                for i in value['filters']:
                    for t in i:
                        f_param_key = 'filter[filters][%s]'% f_param_count
                        f_param_key = f_param_key+'[%s]'%t
                        kwargs[f_param_key] = self._encode(i[t])
                    f_param_count = f_param_count+1
                del kwargs[key]
            else:
                kwargs[key] = self._encode(value)

        if self.key:
            params = dict(
                user=self.user,
                v=self.api_v,
            )
            params.update(kwargs)
            params = self._sortByAlphabet(params)
            params['token'] = self._get_token(self.key, params)

            url = self.url_base + 'key/' + method

        else:
            pass

        data_send = None
        if BODY:
            data_send = json.dumps(BODY)
        else:
            data_send = urllib.urlencode(params)
        data = urllib.urlencode(params)

        if http_method == 'POST':
            file = urllib2.urlopen(url+"?"+data, data_send, timeout=timeout)
        else:

            file = urllib2.urlopen(url+"?"+data, timeout=timeout)

        response = ()
        try:
            response = file.read()
        except:
            pass
        finally:
            file.close()
        return (file.getcode(), response)


class PricePlan(_PricePlanCore):
    def get(self, method, timeout=DEFAULT_TIMEOUT, http_method="POST", **kwargs):
        return self._get(method, timeout, http_method, **kwargs)

    #получаем список переменных
    def getVariables(self):
        return self._get('variables', timeout=DEFAULT_TIMEOUT, http_method="GET")['data']

    #получаем список едениц
    def getMeasures(self):
        return self._get('measures', timeout=DEFAULT_TIMEOUT, http_method="GET")['data']

    def getTypes(self):
        return self._get('types', timeout=DEFAULT_TIMEOUT, http_method="GET")['data']