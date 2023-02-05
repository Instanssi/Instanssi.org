from unittest import mock

import pytest

from Instanssi.common.storage import ASCIIFileSystemStorage


@pytest.mark.parametrize(
    "input_data,expected",
    [
        (".png", "ffffffff.png"),
        ("test.png", "test_ffffffff.png"),
        (" asd.png", "asd_ffffffff.png"),
        ("tämä on testitiedosto.jpg", "tama_on_testitiedosto_ffffffff.jpg"),
        ("SCHEIẞE.zip", "SCHEISsE_ffffffff.zip"),
        ("💩.invalid", "ffffffff.invalid"),
        ("invalid.💩", "invalid_ffffffff"),
        ("../test.png", "test_ffffffff.png"),
        ("   test.png", "test_ffffffff.png"),
        ("test.png/kek.lol", "test.pngkek_ffffffff.lol"),
        ("test.png   ", "test_ffffffff.png"),
    ],
)
@mock.patch("Instanssi.common.storage.token_hex")
def test_storage_string(m, input_data, expected):
    m.return_value = "ffffffff"
    storage = ASCIIFileSystemStorage()
    assert storage.get_valid_name(input_data) == expected
