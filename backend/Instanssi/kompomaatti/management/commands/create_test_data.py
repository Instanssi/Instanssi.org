from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Compo,
    Entry,
    Event,
    Profile,
    Vote,
    VoteCodeRequest,
    VoteGroup,
)

from .fixtures.blog_entries import blog_entries
from .fixtures.competitions import competition_participations, competitions
from .fixtures.compos import compos
from .fixtures.entries import entries
from .fixtures.events import events
from .fixtures.files import (
    get_random_archive_filename,
    get_random_image_filename,
    get_random_video_filename,
)
from .fixtures.profiles import profiles
from .fixtures.users import users
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
