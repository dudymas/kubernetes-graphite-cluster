import os
from cassandra import Cluster
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sets up cassandra if necessary..."

    def handle(self):
        cluster = Cluster(settings.BG_CASSANDRA_CONTACT_POINTS)
        session = cluster.connect()
        session.execute("""
        CREATE KEYSPACE IF NOT EXISTS biggraphite_metadata WITH replication = {
        'class': 'SimpleStrategy',
        'replication_factor': '1'
        } AND durable_writes = true;

        CREATE KEYSPACE IF NOT EXISTS biggraphite WITH replication = {
        'class': 'SimpleStrategy',
        'replication_factor': '1'
        } AND durable_writes = false;
        """)
