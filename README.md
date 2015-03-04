# django-migration-sniffer
flags django migrations for risky operations that may cause downtime or server errors

These are defined as operations that remove fields, drop tables, rename fields,
renames tables or run arbitrary SQL and Python code. 

# Usage

* Install 

* Add 'migration_sniffer' to INSTALLED_APPS.

```
INSTALLED_APPS = (
...
    'migration_sniffer'
)
```

* Run the 'sniff_migrations' command

```
python manage.py sniff_migrations
```
