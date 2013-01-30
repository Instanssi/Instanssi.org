# Template tag for displaying Instanssi's range of quality products.

from django import template
from Instanssi.store.models import StoreItem, StoreTransaction
from Instanssi.store.forms import StoreOrderForm

register = template.Library()


def handleStorePost(request):
    pass


@register.inclusion_tag('store/tags/shop.html')
def render_store(event_id, transaction_form):
    return {
        'transaction_form':
        transaction_form or StoreOrderForm(event_id=event_id),
    }
