import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yubtub.settings")
django.setup()

from app.models import Video, Post, VideoComment, PostComment
from bugs.models import BugReport
from chat.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

ANONYMOUS_SENTINELS = {'anonymoususer', 'anonymous', '', 'system'}

def fix_model_authors(model, field_name='author', do_commit=False):
    """
    Converts CharField author fields (usernames) to integer user IDs.
    Skips anonymous/system entries and records that are already valid IDs.
    """
    qs = model.objects.all()
    total = qs.count()
    print(f"Processing {model.__name__}: {total} records")
    changed = 0

    for obj in qs:
        current = getattr(obj, field_name)

        # Already a valid integer user ID — skip
        if isinstance(current, int):
            try:
                User.objects.get(id=current)
                continue
            except User.DoesNotExist:
                pass  # fall through and try to resolve it

        username = str(current).strip()

        # Skip sentinels like AnonymousUser (common in BugReport)
        if username.lower() in ANONYMOUS_SENTINELS:
            print(f"  Skipping sentinel '{username}' (model={model.__name__}, pk={obj.pk})")
            continue

        # Already a numeric string — try resolving as an ID first
        if username.isdigit():
            try:
                User.objects.get(id=int(username))
                setattr(obj, field_name, int(username))
                if do_commit:
                    obj.save()
                changed += 1
                continue
            except User.DoesNotExist:
                pass  # fall through to username lookup

        # Standard username -> ID lookup
        try:
            user = User.objects.get(username=username)
            setattr(obj, field_name, user.id)
            if do_commit:
                obj.save()
            changed += 1
        except User.DoesNotExist:
            print(f"  No matching user for '{username}' (model={model.__name__}, pk={obj.pk})")
        except Exception as e:
            print(f"  Error for pk={obj.pk}: {e}")

    print(f"Finished {model.__name__}: changed {changed} records\n")
    return changed


def fix_message_fks(do_commit=False):
    """
    Messages use real FK fields (from_user, to_user) that already point to
    User objects, so there's no username->ID conversion needed.
    This just validates that all FK references are still intact and reports
    any broken ones (e.g. from deleted users).
    """
    qs = Message.objects.all()
    total = qs.count()
    print(f"Processing Message: {total} records (FK validation only)")
    broken = 0

    for msg in qs:
        issues = []
        try:
            _ = msg.from_user
        except Exception:
            issues.append('from_user')
        try:
            _ = msg.to_user
        except Exception:
            issues.append('to_user')

        if issues:
            broken += 1
            print(f"  Broken FK(s) {issues} on Message pk={msg.pk}")

    if broken == 0:
        print(f"  All Message FK references are valid.")
    else:
        print(f"  Found {broken} broken Message record(s) — delete them manually or reassign.")

    print(f"Finished Message\n")
    return broken


def run_all(commit=False):
    print("START author -> user id migration\n")

    # CharField author fields — convert username -> user ID
    for mdl in (Video, Post, VideoComment, PostComment, BugReport):
        fix_model_authors(mdl, 'author', do_commit=commit)

    # Message FKs — validate only, no conversion needed
    fix_message_fks(do_commit=commit)

    print("DONE")


if __name__ == "__main__":
    commit_flag = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("commit", "apply", "yes"):
        commit_flag = True

    if commit_flag:
        print("Running in COMMIT mode (changes will be saved).")
    else:
        print("Running in DRY-RUN mode (no changes saved). Use: python migrate.py commit")

    print()
    run_all(commit=commit_flag)