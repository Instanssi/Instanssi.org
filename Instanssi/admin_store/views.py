# Logging related
import logging

from django.db.models import Count
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_store.forms import (
    StoreItemForm,
    StoreItemVariantForm,
    TaItemExportForm,
)
from Instanssi.common.auth import staff_access_required
from Instanssi.common.http import Http403
from Instanssi.kompomaatti.models import Event
from Instanssi.store.models import (
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    TransactionItem,
)

logger = logging.getLogger(__name__)


@staff_access_required
def index(request):
    return admin_render(request, "admin_store/index.html", {})


@staff_access_required
def export(request):
    if request.method == "POST":
        form = TaItemExportForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse("manage-store:transactions_csv", args=(form.cleaned_data["event"],))
            )
    else:
        form = TaItemExportForm()

    return admin_render(request, "admin_store/export.html", {"form": form})


@staff_access_required
def amounts(request):
    item_tree = []

    # TODO: This is a really quickly made thing; needs optimizing.

    for event in Event.objects.iterator():
        counts = (
            TransactionItem.objects.filter(item__event=event)
            .exclude(transaction__time_paid=None)
            .values("item")
            .annotate(Count("item"))
        )
        if not counts:
            continue

        item_list = []
        for c in counts:
            if not c["item"]:
                continue

            # Find item description
            item = StoreItem.objects.get(pk=c["item"])

            # Find available variants (if any) and count them
            variants = (
                TransactionItem.objects.filter(item=c["item"])
                .exclude(transaction__time_paid=None)
                .values("variant")
                .annotate(Count("variant"))
            )
            variant_list = []
            for v in variants:
                if not v["variant"]:
                    continue
                variant = StoreItemVariant.objects.get(pk=v["variant"])
                variant_list.append({"sold_variant": variant, "count": v["variant__count"]})

            # Add everything to a list for template
            item_list.append(
                {
                    "sold_item": item,
                    "count": c["item__count"],
                    "variants": variant_list,
                }
            )

        # Add the event & item list to outgoing template data
        item_tree.append({"event": event, "items": item_list})

    # Render response
    return admin_render(request, "admin_store/amounts.html", {"item_tree": item_tree})


@staff_access_required
def items(request):
    StoreItemFormSet = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=5
    )

    # Handle form data
    if request.method == "POST":
        if not request.user.has_perm("store.add_storeitem"):
            raise Http403

        item_form = StoreItemForm(request.POST, request.FILES)
        variant_formset = StoreItemFormSet(request.POST, prefix="nested", instance=item_form.instance)
        if item_form.is_valid() and variant_formset.is_valid():
            item = item_form.save()
            variant_formset.save()
            logger.info('Store Item "{}" added.'.format(item.name), extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-store:items"))
    else:
        item_form = StoreItemForm()
        variant_formset = StoreItemFormSet(prefix="nested", instance=item_form.instance)

    # Get items
    m_items = StoreItem.objects.all()

    # Render response
    return admin_render(
        request,
        "admin_store/items.html",
        {"items": m_items, "item_form": item_form, "variant_formset": variant_formset},
    )


@staff_access_required
def status(request):
    if not request.user.has_perm("store.view_storetransaction"):
        raise Http403

    transactions = StoreTransaction.objects.all()

    # Render response
    return admin_render(
        request,
        "admin_store/status.html",
        {
            "transactions": transactions,
        },
    )


@staff_access_required
def tis_csv(request, event_id):
    if not request.user.has_perm("store.view_storetransaction"):
        raise Http403

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="instanssi_store.csv"'
    t = loader.get_template("admin_store/tis_csv.txt")
    c = {
        "data": TransactionItem.objects.filter(item__event=event_id, transaction__time_paid__isnull=False),
    }
    response.write(t.render(c))
    return response


@staff_access_required
def tis(request):
    if not request.user.has_perm("store.view_storetransaction"):
        raise Http403

    items = TransactionItem.objects.all()

    # Render response
    return admin_render(
        request,
        "admin_store/tis.html",
        {
            "items": items,
        },
    )


@staff_access_required
def transaction_status(request, transaction_id):
    if not request.user.has_perm("store.view_storetransaction"):
        raise Http403

    # Get transaction
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)

    # Get items
    items = transaction.get_transaction_items()

    # Render response
    return admin_render(
        request,
        "admin_store/transactionstatus.html",
        {
            "transaction_id": int(transaction_id),
            "transaction": transaction,
            "items": items,
        },
    )


@staff_access_required
def edit_item(request, item_id):
    if not request.user.has_perm("store.change_storeitem"):
        raise Http403

    StoreItemFormSet = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=3
    )

    # Get Item
    item = get_object_or_404(StoreItem, pk=item_id)

    # Handle form data
    if request.method == "POST":
        variant_formset = StoreItemFormSet(request.POST, instance=item)
        item_form = StoreItemForm(request.POST, request.FILES, instance=item)
        if item_form.is_valid() and variant_formset.is_valid():
            item_form.save()
            variant_formset.save()
            logger.info('Store Item "{}" edited.'.format(item.name), extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-store:edit_item", args=(item.id,)))
    else:
        item_form = StoreItemForm(instance=item)
        variant_formset = StoreItemFormSet(instance=item)

    # Render response
    return admin_render(
        request,
        "admin_store/itemedit.html",
        {"item_form": item_form, "variant_formset": variant_formset},
    )


@staff_access_required
def delete_item(request, item_id):
    # Check for permissions
    if not request.user.has_perm("store.delete_storeitem"):
        raise Http403

    # Delete entry
    try:
        item = StoreItem.objects.get(id=item_id)
        if item.num_sold() == 0:
            item.delete()
            logger.info('Store Item "{}" deleted.'.format(item.name), extra={"user": request.user})
    except StoreItem.DoesNotExist:
        pass

    return HttpResponseRedirect(reverse("manage-store:items"))
