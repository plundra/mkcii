#!/usr/bin/env python
#
# Copyright (c) 2019 Pontus Lundkvist <p@article.se>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from io import BytesIO

from pycdlib import PyCdlib

SAFE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"


def _safe_name(filename):
    """Make filename safe for ISO9660 (interchange level 3)"""
    return "".join(c if c in SAFE_CHARS else "_" for c in filename.upper())


class EasyISO:
    """Simple wrapper around PyCdlib, just add files"""

    def __init__(self, label):
        """New ISO instance, with volume label"""
        self.iso = PyCdlib()
        self.iso.new(vol_ident=label, rock_ridge="1.09", interchange_level=3)

    def add_file(self, filename, content):
        """Add filename with content to ISO"""
        self.iso.add_fp(
            BytesIO(content),
            len(content),
            iso_path="/" + _safe_name(filename),
            rr_name=filename,
        )

    def get_iso(self):
        """Return ISO as bytes"""
        output = BytesIO()
        self.iso.write_fp(output)
        return output.getvalue()
