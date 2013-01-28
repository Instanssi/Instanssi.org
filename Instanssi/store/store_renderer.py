# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from Instanssi.store.svmlib import svm_request,SVMException
from Instanssi.store.forms import StoreOrderForm
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem

# Logging related
import logging
logger = logging.getLogger(__name__)

# Renders store form, handles requests to Suomen Verkkomaksut
def render_store(request, event_id, domain, success_url, failure_url):
    if request.method == 'POST':
        transaction_form = StoreOrderForm(request.POST, event_id=event_id)

        if transaction_form.is_valid():
            ta = transaction_form.save()

            product_list = []
            for item in TransactionItem.objects.filter(transaction=ta):
                product_list.append({
                    'title': item.item.name,
                    'code': str(item.item.id),
                    'amount': str(item.amount),
                    'price': str(item.item.price),
                    'vat': '0',
                    'type': 1,
                })

            svm_data = {
                'orderNumber': str(ta.id),
                #'currency': 'EUR',
                'locale': 'fi_FI',
                'urlSet': {
                    'success': domain+success_url,
                    'failure': domain+failure_url,
                    'notification': domain+reverse('store:notify'),
                    'pending': '',
                },
                'orderDetails': {
                    'includeVat': 1,
                    'contact': {
                        'telephone': ta.telephone,
                        'mobile': ta.mobile,
                        'email': ta.email,
                        'firstName': ta.firstname,
                        'lastName': ta.lastname,
                        'companyName': ta.company,
                        'address': {
                            'street': ta.street,
                            'postalCode': ta.postalcode,
                            'postalOffice': ta.city,
                            'country': ta.country.code
                        }
                    },
                    'products': product_list,
                },
            }
            
            # Make a request
            msg = None
            try:
                msg = svm_request(settings.VMAKSUT_ID, settings.VMAKSUT_SECRET, svm_data)
            except SVMException as ex:
                a,b = ex.args
                logger.warning('(%s) %s' % (b,a))
                return HttpResponseRedirect(failure_url)
            except Exception as ex:
                logger.warning('%s.' % (ex))
                return HttpResponseRedirect(failure_url)

            # Save token, redirect
            ta.time_created = datetime.now()
            ta.token = msg['token']
            ta.save()
            return HttpResponseRedirect(msg['url'])
    else:
        transaction_form = StoreOrderForm(event_id=event_id)
        
    return {'transaction_form': transaction_form}