from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperAddressPool(ORMWrapper):
    def get_address(self):
        ap = self
        if ap.addresses:
            avail_ips = ap.addresses.split()
        else:
            avail_ips = []

        if ap.inuse:
            inuse_ips = ap.inuse.split()
        else:
            inuse_ips = []

        while avail_ips:
            addr = avail_ips.pop(0)

            if addr in inuse_ips:
                # This may have happened if someone re-ran the tosca
                # recipe and 'refilled' the AddressPool while some addresses
                # were still in use.
                continue

            inuse_ips.insert(0, addr)

            ap.inuse = " ".join(inuse_ips)
            ap.addresses = " ".join(avail_ips)
            return addr

        return None


    def put_address(self, addr):
        ap = self
        addresses = ap.addresses or ""
        parts = addresses.split()
        if addr not in parts:
            parts.insert(0, addr)
            ap.addresses = " ".join(parts)

        inuse = ap.inuse or ""
        parts = inuse.split()
        if addr in parts:
            parts.remove(addr)
            ap.inuse = " ".join(parts)

register_convenience_wrapper("AddressPool", ORMWrapperAddressPool)
