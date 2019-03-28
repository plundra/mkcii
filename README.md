mkcii - Make Cloud-Init ISO
===========================

Early stages in development, but works for me.

Example:
With this and a pristine ubuntu-18.04-minimal-cloudimg-amd64.img image,
I boot a new VM, configure it lightly (add user, setup network, purge a package,
disable cloud-init for next boot, and reboot it), in under 20 seconds.

Using nothing else but qemu, this script and off-the-shelf cloudimage,
if serves my needs very well.

Usage
-----
$ mkcii \
    -H test-vm1 -u myusername -p changeme -g sudo \
    -s "$(cat ~/.id_ed25519.pub)" -s "$(cat ~/myotherkey.pub)" \
    -e enp0s1 -i 10.0.2.200/24 -d 10.0.2.2 -n 10.0.2.3 \
    -o seed.iso


Background
----------
Wanted a quick way to bootstrap VMs in qemu using nocloud cloud-init.
Handwriting files and running genisoimage works, but this seems more organized.


Todo
----
- Add support for ssh-key and make password optional
- Make runcmd pluggable instead of hard-targeted for Ubuntu 18.04
- Use Match statements for network-config to be naming independant
- ???
