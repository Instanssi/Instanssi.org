# Template tag for displaying Instanssi's range of quality products.

from django import template
from Instanssi.store.models import StoreItem, StoreTransaction
from Instanssi.store.forms import StoreTransactionForm

register = template.Library()


def handleStorePost(request):
    pass


@register.inclusion_tag('store/tags/shop.html')
def render_store(event_id, transaction_form):
    items = StoreItem.objects.filter(max__gt=0, available=True,
                                     event_id=event_id)
    display_items = []

    for item in items:
        display_items.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': "%.2f" % item.price
        })

    return {
        'store_items': display_items,
        'transaction_form': transaction_form or StoreTransactionForm(),
    }
