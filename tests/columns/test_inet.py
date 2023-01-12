from ipaddress import IPv6Address, IPv6Interface
from unittest import TestCase

from piccolo.columns.column_types import Inet
from piccolo.table import Table

from ..base import engines_only


class MyTable(Table):
    ip_address = Inet(null=True)


@engines_only("postgres", "cockroach")
class TestInet(TestCase):

    def setUp(self):
        MyTable.create_table().run_sync()

    def tearDown(self):
        MyTable.alter().drop_table().run_sync()

    def test_ipv4_address_subnetmask(self):
        row = MyTable(ip_address="10.1.1.1/32")
        row.save().run_sync()

        with self.assertRaises(Exception):
            row.ip_address = "10.1.1.1/322"
            row.save().run_sync()

    def test_ipv6_address_subnetmask(self):
        ip_address = Inet(null=True)
        row = MyTable(ip_address="2001:db8:3333:4444:5555:6666:1.2.3.4/96")
        row.save().run_sync()

        get_from_db = row.objects().first().run_sync()
        assert get_from_db.ip_address == IPv6Interface('2001:db8:3333:4444:5555:6666:102:304/96')

        row.ip_address = "2001:db8:0:0:0:0:0:0/96"
        row.save().run_sync()

        get_from_db = row.objects().first().run_sync()
        assert get_from_db.ip_address == IPv6Interface('2001:db8::/96')

        with self.assertRaises(Exception):
            row.ip_address = "2001:db8:3333:4444:5555:6666:88/96"
            row.save().run_sync()
