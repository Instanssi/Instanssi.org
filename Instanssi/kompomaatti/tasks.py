from __future__ import absolute_import, unicode_literals
import tarfile
import os
import uuid
import tempfile

from celery import shared_task

from django.core.files import File
from .models import Entry, EntryCollection, Compo


@shared_task
def rebuild_collection(compo_id: int):
    print("Running for compo id {}".format(compo_id))
    compo = Compo.objects.get(id=compo_id)
    entries = Entry.objects.filter(compo_id=compo_id)

    try:
        col = EntryCollection.objects.get(compo=compo)
        col.file.delete()
    except EntryCollection.DoesNotExist:
        col = EntryCollection(compo=compo)

    with tempfile.TemporaryFile() as fd:
        with tarfile.open(fileobj=fd, mode="w:gz") as tar:
            for entry in entries:
                _, ext = os.path.splitext(entry.entryfile.path)
                base_name = '{}-by-{}{}'\
                    .format(entry.name, entry.creator, ext)\
                    .replace(' ', '_')\
                    .encode('ascii', 'ignore')\
                    .decode('ascii')
                print("Compressing to {}".format(base_name))
                with open(entry.entryfile.path, 'rb') as in_fd:
                    tar_info = tarfile.TarInfo(base_name)
                    tar_info.size = entry.entryfile.size
                    tar.addfile(
                        tarinfo=tar_info,
                        fileobj=in_fd)
            tar.close()

        col_name = '{}_{}_{}.tar.gz'.format(
            compo.event.name, compo.name, uuid.uuid4().hex[:6])
        col.file.save(
            name=col_name.encode('ascii', 'ignore').decode('ascii'),
            content=File(fd))
        col.save()
        print(col.compo, col.file, col.updated_at)
