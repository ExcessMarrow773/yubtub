# ...existing code...
import os
import django
import sys

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yubtub.settings")

# Initialize Django
django.setup()

from app.models import Video, Post, VideoComment, PostComment
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_model_authors(model, field_name='author', do_commit=False):
    qs = model.objects.all()
    total = qs.count()
    print(f"Processing {model.__name__}: {total} records")
    changed = 0

    for obj in qs:
        current = getattr(obj, field_name)
        # Skip if already an int and matches a user id
        if isinstance(current, int):
            # if it's an int but not a valid user id, try to resolve via string
            try:
                User.objects.get(id=current)
                continue
            except Exception:
                pass

        username = str(current).strip()
        if not username:
            continue

        # If username looks like a numeric id string, try to convert
        if username.isdigit():
            try:
                user = User.objects.get(id=int(username))
                setattr(obj, field_name, user.id)
                if do_commit:
                    obj.save()
                changed += 1
                continue
            except User.DoesNotExist:
                # fall through to try username lookup
                pass

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

def run_all(commit=False):
    print("START author -> user id migration")
    for mdl in (Video, Post, VideoComment, PostComment):
        fix_model_authors(mdl, 'author', do_commit=commit)
    print("DONE")

if __name__ == "__main__":
    commit_flag = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("commit", "apply", "yes"):
        commit_flag = True

    if commit_flag:
        print("Running in COMMIT mode (changes will be saved).")
    else:
        print("Running in DRY-RUN mode (no changes saved). Use: python migrate.py commit")

    run_all(commit=commit_flag)
# ...existing code...