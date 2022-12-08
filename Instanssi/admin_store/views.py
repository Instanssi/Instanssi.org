import csv
import logging

from django.contrib.auth.decorators import permission_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.db.models import Count
from django.forms import inlineformset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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
from Instanssi.kompomaatti.models import Event
from Instanssi.store.models import (
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    TransactionItem,
)

logger = logging.getLogger(__name__)


@staff_access_required
def index(request: HttpRequest) -> HttpResponse:
    return admin_render(request, "admin_store/index.html", {})


@staff_access_required
def export(request: HttpRequest) -> HttpResponse:
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
def amounts(request: HttpRequest) -> HttpResponse:
    item_tree = []
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

    return admin_render(request, "admin_store/amounts.html", {"item_tree": item_tree})


@staff_access_required
def items(request: HttpRequest) -> HttpResponse:
    store_item_form_set = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=5
    )

    if request.method == "POST":
        if not request.user.has_perm("store.add_storeitem"):
            raise PermissionDenied()

        item_form = StoreItemForm(request.POST, request.FILES)
        variant_formset = store_item_form_set(request.POST, prefix="nested", instance=item_form.instance)
        if item_form.is_valid() and variant_formset.is_valid():
            item = item_form.save()
            variant_formset.save()
            logger.info("Store Item '%s' added.", item.name, extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-store:items"))
    else:
        item_form = StoreItemForm()
        variant_formset = store_item_form_set(prefix="nested", instance=item_form.instance)

    m_items = StoreItem.objects.all()
    return admin_render(
        request,
        "admin_store/items.html",
        {"items": m_items, "item_form": item_form, "variant_formset": variant_formset},
    )


@staff_access_required
@permission_required("store.view_storetransaction", raise_exception=True)
def status(request: HttpRequest) -> HttpResponse:
    return admin_render(request, "admin_store/status.html", {"transactions": StoreTransaction.objects.all()})


@staff_access_required
@permission_required("store.view_storetransaction", raise_exception=True)
def tis_csv(request: HttpRequest, event_id: int) -> HttpResponse:
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="instanssi_entries.csv"'},
    )
    writer = csv.writer(response, dialect="unix")
    writer.writerow(
        [
            "TransaktioID",
            "TuoteID",
            "Aikaleima",
            "Tuotteen nimi",
            "Hinta",
            "Etunimi",
            "Sukunimi",
            "Sähköposti",
            "Toimitettu",
        ]
    )

    transaction_items = TransactionItem.objects.filter(
        item__event=event_id, transaction__time_paid__isnull=False
    )
    for tx in transaction_items:
        writer.writerow(
            [
                tx.transaction_id,
                tx.item_id,
                tx.transaction.time_created.isoformat(),
                tx.item.name,
                tx.purchase_price,
                tx.transaction.firstname,
                tx.transaction.lastname,
                tx.transaction.email,
                tx.is_delivered,
            ]
        )

    return response


@staff_access_required
@permission_required("store.view_storetransaction", raise_exception=True)
def tis(request: HttpRequest) -> HttpResponse:
    return admin_render(request, "admin_store/tis.html", {"items": TransactionItem.objects.all()})


@staff_access_required
@permission_required("store.view_storetransaction", raise_exception=True)
def transaction_status(request: HttpRequest, transaction_id: int) -> HttpResponse:
    transaction = get_object_or_404(StoreTransaction, pk=transaction_id)
    transaction_items = transaction.get_transaction_items()
    return admin_render(
        request,
        "admin_store/transactionstatus.html",
        {
            "transaction_id": transaction_id,
            "transaction": transaction,
            "items": transaction_items,
        },
    )


@staff_access_required
@permission_required("store.change_storeitem", raise_exception=True)
def edit_item(request: HttpRequest, item_id: int) -> HttpResponse:
    store_item_form_set = inlineformset_factory(
        parent_model=StoreItem, model=StoreItemVariant, form=StoreItemVariantForm, extra=3
    )
    item = get_object_or_404(StoreItem, pk=item_id)

    if request.method == "POST":
        variant_formset = store_item_form_set(request.POST, instance=item)
        item_form = StoreItemForm(request.POST, request.FILES, instance=item)
        if item_form.is_valid() and variant_formset.is_valid():
            item_form.save()
            variant_formset.save()
            logger.info("Store Item '%s' edited.", item.name, extra={"user": request.user})
            return HttpResponseRedirect(reverse("manage-store:edit_item", args=(item.id,)))
    else:
        item_form = StoreItemForm(instance=item)
        variant_formset = store_item_form_set(instance=item)

    return admin_render(
        request,
        "admin_store/itemedit.html",
        {"item_form": item_form, "variant_formset": variant_formset},
    )


@staff_access_required
@permission_required("store.delete_storeitem", raise_exception=True)
def delete_item(request, item_id):
    item = get_object_or_404(StoreItem, pk=item_id)
    if item.num_sold() > 0:
        raise BadRequest()
    item.delete()
    logger.info("Store Item '%s' deleted.", item.name, extra={"user": request.user})
    return HttpResponseRedirect(reverse("manage-store:items"))
