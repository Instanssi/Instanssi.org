from pathlib import Path
from secrets import token_hex

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from Instanssi.arkisto.models import OtherVideo, OtherVideoCategory
from Instanssi.common.youtube.parser import YoutubeURL
from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    Profile,
    TicketVoteCode,
    Vote,
    VoteCodeRequest,
    VoteGroup,
)
from Instanssi.store.models import (
    Receipt,
    StoreItem,
    StoreItemVariant,
    StoreTransaction,
    StoreTransactionEvent,
    TransactionItem,
)

from .fixtures.blog_entries import blog_entries
from .fixtures.competitions import competition_participations, competitions
from .fixtures.compos import compos
from .fixtures.entries import entries
from .fixtures.events import events
from .fixtures.files import (
    get_random_archive_filename,
    get_random_image_filename,
    get_random_ticket_product_image_filename,
    get_random_tshirt_product_image_filename,
    get_random_video_filename,
)
from .fixtures.profiles import profiles
from .fixtures.store_items import store_item_variants, store_items
from .fixtures.store_transactions import (
    store_transactions,
    ticket_vote_codes,
    transaction_items,
)
from .fixtures.users import users
from .fixtures.videos import video_categories, videos
from .fixtures.votecodes import vote_code_requests
from .fixtures.votes import vote_groups, votes


class Command(BaseCommand):
    help = """Create test data for kompomaatti

    Note: This command does NOT require Redis/Celery to be running. It bypasses the
    Entry.save() method that normally triggers async tasks for generating alternate audio files.
    """

    def __init__(self):
        super().__init__()
        self.created_users = {}
        self.created_events = {}
        self.created_compos = {}
        self.created_entries = {}
        self.created_vote_groups = []
        self.created_competitions = {}
        self.created_store_items = {}
        self.created_transactions = {}
        self.created_transaction_items = {}
        self.created_video_categories = {}

    def setup_users(self) -> None:
        """Create test users - password is same as username"""
        self.stdout.write("Creating users...")
        for user_data in users:
            username = user_data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  User {username} already exists, skipping...")
                self.created_users[username] = User.objects.get(username=username)
                continue

            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password=username,  # Password is same as username
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_staff=user_data["is_staff"],
                is_superuser=user_data["is_superuser"],
            )
            self.created_users[username] = user
            self.stdout.write(f"  Created user: {username} (password: {username})")

    def setup_profiles(self) -> None:
        """Create user profiles"""
        self.stdout.write("Creating profiles...")
        for profile_data in profiles:
            username = profile_data["user_username"]
            user = self.created_users.get(username)
            if not user:
                self.stderr.write(f"  User {username} not found, skipping profile...")
                continue

            if Profile.objects.filter(user=user).exists():
                self.stdout.write(f"  Profile for {username} already exists, skipping...")
                continue

            Profile.objects.create(user=user, otherinfo=profile_data["otherinfo"])
            self.stdout.write(f"  Created profile for: {username}")

    def setup_events(self) -> None:
        """Create events"""
        self.stdout.write("Creating events...")
        for event_data in events:
            event_pk = event_data["pk"]
            if Event.objects.filter(pk=event_pk).exists():
                self.stdout.write(f"  Event {event_data['name']} already exists, skipping...")
                self.created_events[event_pk] = Event.objects.get(pk=event_pk)
                continue

            event = Event.objects.create(**event_data)
            self.created_events[event_pk] = event
            self.stdout.write(f"  Created event: {event.name}")

    def setup_compos(self) -> None:
        """Create compos"""
        self.stdout.write("Creating compos...")
        for compo_data in compos:
            event_pk = compo_data.pop("event_pk")
            event = self.created_events.get(event_pk)
            if not event:
                self.stderr.write(f"  Event {event_pk} not found, skipping compo...")
                continue

            compo_name = compo_data["name"]
            if Compo.objects.filter(event=event, name=compo_name).exists():
                self.stdout.write(f"  Compo {compo_name} for event {event.name} already exists, skipping...")
                self.created_compos[(event_pk, compo_name)] = Compo.objects.get(event=event, name=compo_name)
                continue

            compo = Compo.objects.create(event=event, **compo_data)
            self.created_compos[(event_pk, compo_name)] = compo
            self.stdout.write(f"  Created compo: {compo.name} for {event.name}")

    def get_test_file(self, file_type: str) -> File:
        """Get a test file of the specified type"""
        if file_type == "image":
            filepath = get_random_image_filename()
        elif file_type == "video":
            filepath = get_random_video_filename()
        elif file_type == "archive":
            filepath = get_random_archive_filename()
        elif file_type == "ticket":
            filepath = get_random_ticket_product_image_filename()
        elif file_type == "tshirt":
            filepath = get_random_tshirt_product_image_filename()
        else:
            raise ValueError(f"Unknown file type: {file_type}")

        return File(open(filepath, "rb"), name=Path(filepath).name)

    def setup_entries(self) -> None:
        """Create entries"""
        self.stdout.write("Creating entries...")
        for entry_data in entries:
            compo_name = entry_data.pop("compo_name")
            compo_event_pk = entry_data.pop("compo_event_pk")
            user_username = entry_data.pop("user_username")

            compo = self.created_compos.get((compo_event_pk, compo_name))
            user = self.created_users.get(user_username)

            if not compo:
                self.stderr.write(f"  Compo {compo_name} not found, skipping entry...")
                continue
            if not user:
                self.stderr.write(f"  User {user_username} not found, skipping entry...")
                continue

            entry_name = entry_data["name"]
            if Entry.objects.filter(compo=compo, name=entry_name).exists():
                self.stdout.write(f"  Entry {entry_name} already exists, skipping...")
                existing_entry = Entry.objects.get(compo=compo, name=entry_name)
                self.created_entries[entry_name] = existing_entry
                continue

            # Handle file fields
            entryfile_type = entry_data.pop("entryfile")
            sourcefile_type = entry_data.pop("sourcefile")
            imagefile_type = entry_data.pop("imagefile_original")

            entry = Entry(compo=compo, user=user, **entry_data)

            # Attach files
            if entryfile_type:
                entry.entryfile = self.get_test_file(entryfile_type)
            if sourcefile_type:
                entry.sourcefile = self.get_test_file(sourcefile_type)
            if imagefile_type:
                entry.imagefile_original = self.get_test_file(imagefile_type)

            # Save without triggering async generate_alternates (to avoid requiring Redis)
            # We call the parent Model.save() to skip Entry.save() which triggers async tasks
            from django.db.models import Model

            Model.save(entry)

            self.created_entries[entry_name] = entry
            self.stdout.write(f"  Created entry: {entry.name} by {entry.creator}")

    def setup_votes(self) -> None:
        """Create vote groups and votes"""
        self.stdout.write("Creating vote groups and votes...")

        # Create vote groups
        for group_data in vote_groups:
            user_username = group_data["user_username"]
            compo_name = group_data["compo_name"]
            compo_event_pk = group_data["compo_event_pk"]

            user = self.created_users.get(user_username)
            compo = self.created_compos.get((compo_event_pk, compo_name))

            if not user or not compo:
                self.stderr.write(f"  User or compo not found for vote group, skipping...")
                continue

            if VoteGroup.objects.filter(user=user, compo=compo).exists():
                self.stdout.write(
                    f"  Vote group for {user_username} in {compo_name} already exists, skipping..."
                )
                self.created_vote_groups.append(VoteGroup.objects.get(user=user, compo=compo))
                continue

            vote_group = VoteGroup.objects.create(user=user, compo=compo)
            self.created_vote_groups.append(vote_group)
            self.stdout.write(f"  Created vote group for {user_username} in {compo_name}")

        # Create individual votes
        for vote_data in votes:
            group_index = vote_data["group_index"]
            entry_name = vote_data["entry_name"]
            rank = vote_data["rank"]

            if group_index >= len(self.created_vote_groups):
                self.stderr.write(f"  Vote group index {group_index} out of range, skipping vote...")
                continue

            vote_group = self.created_vote_groups[group_index]
            entry = self.created_entries.get(entry_name)

            if not entry:
                self.stderr.write(f"  Entry {entry_name} not found, skipping vote...")
                continue

            if Vote.objects.filter(user=vote_group.user, compo=vote_group.compo, entry=entry).exists():
                self.stdout.write(f"  Vote already exists, skipping...")
                continue

            Vote.objects.create(
                user=vote_group.user, compo=vote_group.compo, entry=entry, rank=rank, group=vote_group
            )
            self.stdout.write(f"  Created vote: {entry.name} ranked {rank} by {vote_group.user.username}")

    def setup_competitions(self) -> None:
        """Create competitions"""
        self.stdout.write("Creating competitions...")
        for comp_data in competitions:
            event_pk = comp_data.pop("event_pk")
            event = self.created_events.get(event_pk)

            if not event:
                self.stderr.write(f"  Event {event_pk} not found, skipping competition...")
                continue

            comp_name = comp_data["name"]
            if Competition.objects.filter(event=event, name=comp_name).exists():
                self.stdout.write(f"  Competition {comp_name} already exists, skipping...")
                self.created_competitions[(event_pk, comp_name)] = Competition.objects.get(
                    event=event, name=comp_name
                )
                continue

            competition = Competition.objects.create(event=event, **comp_data)
            self.created_competitions[(event_pk, comp_name)] = competition
            self.stdout.write(f"  Created competition: {competition.name}")

    def setup_competition_participations(self) -> None:
        """Create competition participations"""
        self.stdout.write("Creating competition participations...")
        for part_data in competition_participations:
            comp_name = part_data.pop("competition_name")
            comp_event_pk = part_data.pop("competition_event_pk")
            user_username = part_data.pop("user_username")

            competition = self.created_competitions.get((comp_event_pk, comp_name))
            user = self.created_users.get(user_username)

            if not competition or not user:
                self.stderr.write(f"  Competition or user not found, skipping participation...")
                continue

            if CompetitionParticipation.objects.filter(competition=competition, user=user).exists():
                self.stdout.write(f"  Participation already exists, skipping...")
                continue

            CompetitionParticipation.objects.create(competition=competition, user=user, **part_data)
            self.stdout.write(f"  Created participation: {part_data['participant_name']} in {comp_name}")

    def setup_vote_code_requests(self) -> None:
        """Create vote code requests"""
        self.stdout.write("Creating vote code requests...")
        for req_data in vote_code_requests:
            event_pk = req_data.pop("event_pk")
            user_username = req_data.pop("user_username")

            event = self.created_events.get(event_pk)
            user = self.created_users.get(user_username)

            if not event or not user:
                self.stderr.write(f"  Event or user not found, skipping vote code request...")
                continue

            if VoteCodeRequest.objects.filter(event=event, user=user).exists():
                self.stdout.write(f"  Vote code request already exists, skipping...")
                continue

            VoteCodeRequest.objects.create(event=event, user=user, **req_data)
            self.stdout.write(f"  Created vote code request for {user_username}")

    def setup_blog_entries(self) -> None:
        """Create blog entries"""
        self.stdout.write("Creating blog entries...")
        for blog_data in blog_entries:
            event_pk = blog_data.pop("event_pk")
            user_username = blog_data.pop("user_username")

            event = self.created_events.get(event_pk)
            user = self.created_users.get(user_username)

            if not event or not user:
                self.stderr.write(f"  Event or user not found, skipping blog entry...")
                continue

            title = blog_data["title"]
            if BlogEntry.objects.filter(event=event, title=title).exists():
                self.stdout.write(f"  Blog entry '{title}' already exists, skipping...")
                continue

            BlogEntry.objects.create(event=event, user=user, **blog_data)
            visibility = "public" if blog_data["public"] else "draft"
            self.stdout.write(f"  Created blog entry: {title} ({visibility})")

    def setup_store_items(self) -> None:
        """Create store items"""
        self.stdout.write("Creating store items...")
        for item_data in store_items:
            event_pk = item_data.pop("event_pk")
            imagefile_type = item_data.pop("imagefile_type", None)
            event = self.created_events.get(event_pk)

            if not event:
                self.stderr.write(f"  Event {event_pk} not found, skipping store item...")
                continue

            item_name = item_data["name"]
            if StoreItem.objects.filter(event=event, name=item_name).exists():
                self.stdout.write(f"  Store item '{item_name}' already exists, skipping...")
                self.created_store_items[(event_pk, item_name)] = StoreItem.objects.get(
                    event=event, name=item_name
                )
                continue

            # Create the store item
            store_item = StoreItem(event=event, **item_data)

            # Attach image file if specified
            if imagefile_type:
                store_item.imagefile_original = self.get_test_file(imagefile_type)

            store_item.save()
            self.created_store_items[(event_pk, item_name)] = store_item
            item_type = "ticket" if store_item.is_ticket else "merchandise"
            secret = " (secret)" if store_item.is_secret else ""
            image_status = " with image" if imagefile_type else ""
            self.stdout.write(f"  Created store item: {item_name} ({item_type}){secret}{image_status}")

    def setup_store_item_variants(self) -> None:
        """Create store item variants"""
        self.stdout.write("Creating store item variants...")
        for variant_data in store_item_variants:
            item_event_pk = variant_data["item_event_pk"]
            item_name = variant_data["item_name"]
            variant_name = variant_data["variant_name"]

            store_item = self.created_store_items.get((item_event_pk, item_name))
            if not store_item:
                self.stderr.write(f"  Store item {item_name} not found, skipping variant...")
                continue

            if StoreItemVariant.objects.filter(item=store_item, name=variant_name).exists():
                self.stdout.write(f"  Variant '{variant_name}' for {item_name} already exists, skipping...")
                continue

            StoreItemVariant.objects.create(item=store_item, name=variant_name)
            self.stdout.write(f"  Created variant: {item_name} - {variant_name}")

    def setup_store_transactions(self) -> None:
        """Create store transactions"""
        self.stdout.write("Creating store transactions...")
        for trans_data in store_transactions:
            transaction_id = trans_data.pop("transaction_id")
            event_pk = trans_data.pop("event_pk")
            user_username = trans_data.pop("user_username")

            event = self.created_events.get(event_pk)
            if not event:
                self.stderr.write(f"  Event {event_pk} not found, skipping transaction...")
                continue

            user = self.created_users.get(user_username) if user_username else None

            # Generate unique key and token
            key = token_hex(20)  # 40 character hex string
            token = f"test_{transaction_id}"

            # Check if transaction already exists by email and event
            existing = StoreTransaction.objects.filter(
                email=trans_data["email"], time_created=trans_data["time_created"]
            ).first()
            if existing:
                self.stdout.write(
                    f"  Transaction for {trans_data['email']} at {trans_data['time_created']} already exists, skipping..."
                )
                self.created_transactions[transaction_id] = existing
                continue

            transaction = StoreTransaction.objects.create(key=key, token=token, **trans_data)
            self.created_transactions[transaction_id] = transaction
            status = "paid" if transaction.is_paid else "pending" if transaction.is_pending else "cancelled"
            self.stdout.write(f"  Created transaction: {transaction.full_name} ({status})")

    def setup_transaction_items(self) -> None:
        """Create transaction items"""
        self.stdout.write("Creating transaction items...")
        for item_data in transaction_items:
            transaction_id = item_data["transaction_id"]
            item_event_pk = item_data["item_event_pk"]
            item_name = item_data["item_name"]
            variant_name = item_data.get("variant_name")
            quantity = item_data["quantity"]
            original_price = item_data["original_price"]
            purchase_price = item_data["purchase_price"]
            time_delivered = item_data.get("time_delivered")

            transaction = self.created_transactions.get(transaction_id)
            store_item = self.created_store_items.get((item_event_pk, item_name))

            if not transaction or not store_item:
                self.stderr.write(f"  Transaction or store item not found, skipping transaction item...")
                continue

            variant = None
            if variant_name:
                variant = StoreItemVariant.objects.filter(item=store_item, name=variant_name).first()
                if not variant:
                    self.stderr.write(f"  Variant {variant_name} not found, skipping transaction item...")
                    continue

            # Create the specified quantity of items
            created_items = []
            for i in range(quantity):
                # Generate unique key for each item
                item_key = token_hex(20)

                # Check if item already exists
                if TransactionItem.objects.filter(key=item_key).exists():
                    # Regenerate key if collision (very unlikely)
                    item_key = token_hex(20)

                t_item = TransactionItem.objects.create(
                    key=item_key,
                    item=store_item,
                    variant=variant,
                    transaction=transaction,
                    purchase_price=purchase_price,
                    original_price=original_price,
                    time_delivered=time_delivered,
                )
                created_items.append(t_item)

            # Store items for later reference in ticket vote codes
            if transaction_id not in self.created_transaction_items:
                self.created_transaction_items[transaction_id] = {}
            if (item_event_pk, item_name) not in self.created_transaction_items[transaction_id]:
                self.created_transaction_items[transaction_id][(item_event_pk, item_name)] = []
            self.created_transaction_items[transaction_id][(item_event_pk, item_name)].extend(created_items)

            variant_str = f" ({variant_name})" if variant_name else ""
            self.stdout.write(
                f"  Created {quantity}x {item_name}{variant_str} for transaction {transaction.full_name}"
            )

    def setup_ticket_vote_codes(self) -> None:
        """Create ticket vote codes linking tickets to voting rights"""
        self.stdout.write("Creating ticket vote codes...")
        for vote_code_data in ticket_vote_codes:
            transaction_id = vote_code_data["transaction_id"]
            item_event_pk = vote_code_data["item_event_pk"]
            item_name = vote_code_data["item_name"]
            item_index = vote_code_data["item_index"]
            user_username = vote_code_data["user_username"]
            time = vote_code_data["time"]

            user = self.created_users.get(user_username)
            event = self.created_events.get(item_event_pk)

            if not user or not event:
                self.stderr.write(f"  User or event not found, skipping ticket vote code...")
                continue

            # Get the specific transaction item
            items_list = self.created_transaction_items.get(transaction_id, {}).get(
                (item_event_pk, item_name), []
            )
            if item_index >= len(items_list):
                self.stderr.write(
                    f"  Transaction item index {item_index} out of range, skipping ticket vote code..."
                )
                continue

            ticket_item = items_list[item_index]

            # Check if vote code already exists for this ticket or user+event combination
            if TicketVoteCode.objects.filter(ticket=ticket_item).exists():
                self.stdout.write(
                    f"  Ticket vote code for ticket {ticket_item.key} already exists, skipping..."
                )
                continue

            if TicketVoteCode.objects.filter(event=event, associated_to=user).exists():
                self.stdout.write(
                    f"  Ticket vote code for {user_username} at {event.name} already exists, skipping..."
                )
                continue

            TicketVoteCode.objects.create(event=event, associated_to=user, ticket=ticket_item, time=time)
            self.stdout.write(f"  Created ticket vote code: {item_name} for {user_username} at {event.name}")

    def setup_receipts(self) -> None:
        """Create receipts for all transactions"""
        self.stdout.write("Creating receipts...")
        for transaction in self.created_transactions.values():
            # Check if receipt already exists for this transaction
            if Receipt.objects.filter(transaction=transaction).exists():
                self.stdout.write(f"  Receipt for {transaction.full_name} already exists, skipping...")
                continue

            # Determine sent time - use time_paid for paid transactions, None otherwise
            sent_time = transaction.time_paid

            # Create receipt
            receipt = Receipt.objects.create(
                transaction=transaction,
                subject=f"Instanssi - Tilausvahvistus #{transaction.id}",
                mail_to=transaction.email,
                mail_from="noreply@instanssi.org",
                sent=sent_time,
                params=None,
                content=f"Test receipt content for transaction {transaction.id}",
            )
            status = "sent" if sent_time else "not sent"
            self.stdout.write(f"  Created receipt for {transaction.full_name} ({status})")

    def setup_transaction_events(self) -> None:
        """Create transaction event logs"""
        self.stdout.write("Creating transaction events...")
        for transaction in self.created_transactions.values():
            # Check if events already exist for this transaction
            if StoreTransactionEvent.objects.filter(transaction=transaction).exists():
                self.stdout.write(f"  Events for {transaction.full_name} already exist, skipping...")
                continue

            events_created = 0

            # Event 1: Transaction created
            StoreTransactionEvent.objects.create(
                transaction=transaction,
                message="Transaction created",
                data={"source": "store", "email": transaction.email},
                created=transaction.time_created,
            )
            events_created += 1

            # Event 2: Payment pending (if applicable)
            if transaction.time_pending:
                StoreTransactionEvent.objects.create(
                    transaction=transaction,
                    message="Payment initiated - redirecting to payment provider",
                    data={"provider": "paytrail", "method": transaction.payment_method_name or "unknown"},
                    created=transaction.time_pending,
                )
                events_created += 1

            # Event 3: Payment confirmed or cancelled
            if transaction.time_paid:
                StoreTransactionEvent.objects.create(
                    transaction=transaction,
                    message="Payment confirmed by provider",
                    data={
                        "provider": "paytrail",
                        "status": "ok",
                        "reference": f"REF-{transaction.id:06d}",
                        "amount": str(transaction.get_total_price()),
                    },
                    created=transaction.time_paid,
                )
                events_created += 1
            elif transaction.time_cancelled:
                StoreTransactionEvent.objects.create(
                    transaction=transaction,
                    message="Payment cancelled or failed",
                    data={
                        "provider": "paytrail",
                        "status": "fail",
                        "reason": "User cancelled payment",
                    },
                    created=transaction.time_cancelled,
                )
                events_created += 1

            self.stdout.write(f"  Created {events_created} events for {transaction.full_name}")

    def setup_video_categories(self) -> None:
        """Create video categories for archive"""
        self.stdout.write("Creating video categories...")
        for cat_data in video_categories:
            event_pk = cat_data["event_pk"]
            cat_name = cat_data["name"]

            event = self.created_events.get(event_pk)
            if not event:
                self.stderr.write(f"  Event {event_pk} not found, skipping video category...")
                continue

            if OtherVideoCategory.objects.filter(event=event, name=cat_name).exists():
                self.stdout.write(
                    f"  Video category '{cat_name}' for {event.name} already exists, skipping..."
                )
                self.created_video_categories[(event_pk, cat_name)] = OtherVideoCategory.objects.get(
                    event=event, name=cat_name
                )
                continue

            category = OtherVideoCategory.objects.create(event=event, name=cat_name)
            self.created_video_categories[(event_pk, cat_name)] = category
            self.stdout.write(f"  Created video category: {cat_name} for {event.name}")

    def setup_videos(self) -> None:
        """Create videos for archive"""
        self.stdout.write("Creating videos...")
        for video_data in videos:
            cat_event_pk = video_data["category_event_pk"]
            cat_name = video_data["category_name"]
            video_name = video_data["name"]

            category = self.created_video_categories.get((cat_event_pk, cat_name))
            if not category:
                self.stderr.write(f"  Category {cat_name} not found, skipping video...")
                continue

            if OtherVideo.objects.filter(category=category, name=video_name).exists():
                self.stdout.write(f"  Video '{video_name}' already exists, skipping...")
                continue

            # Build YoutubeURL object
            youtube_url = None
            if video_data.get("youtube_video_id"):
                youtube_url = YoutubeURL(
                    video_id=video_data["youtube_video_id"],
                    start=video_data.get("youtube_start"),
                )

            OtherVideo.objects.create(
                category=category,
                name=video_name,
                description=video_data["description"],
                youtube_url=youtube_url,
            )
            self.stdout.write(f"  Created video: {video_name} in {cat_name}")

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            self.stderr.write("Command disabled in production! settings.DEBUG must be True.")
            return

        try:
            with transaction.atomic():
                self.setup_users()
                self.setup_profiles()
                self.setup_events()
                self.setup_compos()
                self.setup_entries()
                self.setup_votes()
                self.setup_competitions()
                self.setup_competition_participations()
                self.setup_vote_code_requests()
                self.setup_blog_entries()
                self.setup_store_items()
                self.setup_store_item_variants()
                self.setup_store_transactions()
                self.setup_transaction_items()
                self.setup_ticket_vote_codes()
                self.setup_receipts()
                self.setup_transaction_events()
                self.setup_video_categories()
                self.setup_videos()

                self.stdout.write(self.style.SUCCESS("\nData loading complete!"))
                self.stdout.write("\nTest user credentials (password = username):")
                self.stdout.write("  admin / admin")
                self.stdout.write("  testuser1 / testuser1")
                self.stdout.write("  testuser2 / testuser2")
                self.stdout.write("  voter1 / voter1")
                self.stdout.write("  voter2 / voter2")

        except IntegrityError as e:
            self.stderr.write(f"Error loading test data: {e}")
            self.stderr.write(
                "Some test data may already be loaded. Delete existing data or use a fresh database."
            )
        except Exception as e:
            self.stderr.write(f"Unexpected error: {e}")
            raise
