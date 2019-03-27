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

import argparse
import sys
from io import BytesIO
from string import ascii_uppercase

import yaml
from pycdlib import PyCdlib


class CloudInitISO:
    def __init__(self, hostname):
        self.hostname = hostname
        self.network = dict(version=2, ethernets={})
        self.users = []
        self.userdata = {}
        self.metadata = {}

        self.iso = PyCdlib()
        self.iso.new(vol_ident="cidata", rock_ridge="1.09", interchange_level=3)

    def add_user(self, name, passwd, shell="/bin/bash", locked=False, groups=[]):
        user = dict(name=name, shell=shell, lock_passwd=locked, groups=groups)

        # Assume hashed password if it starts with and has multiple dollar signs
        if passwd.startswith("$") and passwd.count("$") >= 2:
            user.update(dict(passwd="passwd"))
        else:
            user.update(dict(plain_text_passwd=passwd))
        self.users.append(user)

    def add_ethernet(self, eth, addresses, gateway=None, nameservers=None):
        ethernet = dict(dhcp4=False, addresses=addresses)

        if gateway:
            ethernet.update(dict(gateway4=gateway))
        if nameservers:
            ethernet.update(dict(nameservers=dict(addresses=nameservers)))

        self.network["ethernets"][eth] = ethernet

    def _add_file(self, filename, content):
        iso_name = "/" + "".join(
            c if c in ascii_uppercase else "_" for c in filename.upper()
        )
        self.iso.add_fp(
            BytesIO(content), len(content), iso_path=iso_name, rr_name=filename
        )

    def _gen_userdata(self):
        self.userdata["users"] = self.users
        self.userdata["final_message"] = "### BOOTED ###"
        self.userdata["power_state"] = dict(mode="reboot")
        self.userdata["runcmd"] = [
            ["apt", "purge", "-y", "snapd"],
            [
                "systemctl",
                "disable",
                "cloud-init",
                "cloud-init-local",
                "cloud-config",
                "cloud-final",
            ],
        ]

    def _gen_metadata(self):
        self.metadata["local-hostname"] = self.hostname

    def dump(self, fp):
        # Pupulate user-data
        self._gen_userdata()
        self._add_file(
            "user-data", b"#cloud-config\n" + yaml.dump(self.userdata).encode("utf-8")
        )

        # Pupulate meta-data
        self._gen_metadata()
        self._add_file("meta-data", yaml.dump(self.metadata).encode("utf-8"))

        # Pupulate network-config
        self._add_file("network-config", yaml.dump(self.network).encode("utf-8"))

        self.iso.write_fp(fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cloud-init cidata iso")
    parser.add_argument("-o", dest="output")
    parser.add_argument("-H", dest="hostname", required=True)
    parser.add_argument("-u", dest="username", required=True)
    parser.add_argument("-g", dest="group", action="append")
    parser.add_argument("-p", dest="passwd", required=True)
    parser.add_argument("-e", dest="ethernet")
    parser.add_argument("-i", dest="cidr", metavar="IPV4/NN", action="append")
    parser.add_argument("-d", dest="gateway")
    parser.add_argument("-n", dest="nameserver", action="append")

    args = parser.parse_args()

    if args.ethernet and not args.cidr:
        parser.error("-e requires -i to be set")

    CII = CloudInitISO(hostname=args.hostname)
    CII.add_user(args.username, args.passwd, groups=args.group)

    # Handle ethernet interfaces
    if args.ethernet:
        extras = {}
        if args.gateway:
            extras.update(dict(gateway=args.gateway))
        if args.nameserver:
            extras.update(dict(nameservers=args.nameserver))

        CII.add_ethernet(args.ethernet, args.cidr, **extras)

    output = None
    if args.output:
        output = open(args.output, "wb")
    elif not sys.stdout.isatty():
        output = sys.stdout.buffer

    if output:
        CII.dump(output)
    else:
        print("Won't write data to terminal (redirect or specify -o)")
        exit(1)
