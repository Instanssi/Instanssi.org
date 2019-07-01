import os
from rest_framework.serializers import ValidationError


class CompoEntrySerializerMixin(object):
    @staticmethod
    def validate_imagefile(data, compo):
        """ Validate imagefile """

        # Aggro if image field is missing but required
        if not data.get('imagefile_original') and compo.is_imagefile_required:
            raise ValidationError({'imagefile_original': ["Kuvatiedosto tarvitaan tälle kompolle"]})

        # Also aggro if image field is supplied but not allowed
        if data.get('imagefile_original') and not compo.is_imagefile_allowed:
            raise ValidationError({'imagefile_original': ["Kuvatiedostoa ei tarvita tälle kompolle"]})

    @staticmethod
    def _maybe_copy_entry_to_image(instance):
        """ If necessary, copy entryfile to imagefile for thumbnail data """
        if instance.compo.is_imagefile_copied:
            name = str('th_' + os.path.basename(instance.entryfile.name))
            instance.imagefile_original.save(name, instance.entryfile)
