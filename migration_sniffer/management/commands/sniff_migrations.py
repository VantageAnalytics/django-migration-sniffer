# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from optparse import make_option
from collections import OrderedDict
from importlib import import_module
import itertools
import traceback

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.core.management.sql import custom_sql_for_model, emit_post_migrate_signal, emit_pre_migrate_signal
from django.db import connections, router, transaction, DEFAULT_DB_ALIAS
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader, AmbiguityError
from django.db.migrations.state import ProjectState
from django.db.migrations.autodetector import MigrationAutodetector

from django.db.migrations.operations import (RunSQL, RunPython, RemoveField, 
    RenameField, DeleteModel, RenameModel)
RISKY_OPERATIONS = (RunSQL, RunPython, RemoveField, RenameField,
    DeleteModel, RenameModel)

from django.utils.module_loading import module_has_submodule


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to synchronize. '
                'Defaults to the "default" database.'),
        make_option('--all', '-a', action='store_true', dest='all', default=False,
            help='Also show applied risky migrations'),
    )

    help = "Print a list of risky unapplied migrations"
    args = "[app_label] [migration_name]"

    def handle(self, *args, **options):

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            if module_has_submodule(app_config.module, "management"):
                import_module('.management', app_config.name)

        # Get the database we're operating from
        db = options.get('database')
        connection = connections[db]

        # If they asked for a migration listing, quit main execution flow and show it
        show_all = options.get("all", False)
        return self.show_risky_migration_list(connection, args, show_all)

    def show_risky_migration_list(self, connection, app_names=None, show_all=False):
        """
        Shows a list of all migrations on the system, or only those of
        some named apps.
        """
        # Load migrations from disk/DB
        loader = MigrationLoader(connection, ignore_no_migrations=True)
        graph = loader.graph
        # If we were passed a list of apps, validate it
        if app_names:
            invalid_apps = []
            for app_name in app_names:
                if app_name not in loader.migrated_apps:
                    invalid_apps.append(app_name)
            if invalid_apps:
                raise CommandError("No migrations present for: %s" % (", ".join(invalid_apps)))
        # Otherwise, show all apps in alphabetic order
        else:
            app_names = sorted(loader.migrated_apps)
        # For each app, print its migrations in order from oldest (roots) to
        # newest (leaves).
        for app_name in app_names:
            shown = set()
            for node in graph.leaf_nodes(app_name):
                for plan_node in graph.forwards_plan(node):
                    if plan_node not in shown and plan_node[0] == app_name:
                        # Give it a nice title if it's a squashed one
                        title = plan_node[1]
                        if graph.nodes[plan_node].replaces:
                            title += " (%s squashed migrations)" % len(graph.nodes[plan_node].replaces)

                        migration = loader.get_migration(app_name, plan_node[1])
                        is_risky = any([isinstance(operation, RISKY_OPERATIONS) for
                            operation in migration.operations])

                        if is_risky:
                            if plan_node in loader.applied_migrations:
                                if show_all:
                                    self.stdout.write(" [x] %s %s" % (app_name, title))
                            else:
                                self.stdout.write(" [ ] %s %s" % (app_name, title))

                        shown.add(plan_node)
