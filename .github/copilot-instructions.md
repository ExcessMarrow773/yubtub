# YubTub AI Development Guide

## Project Overview
YubTub is a Django-based video and post sharing platform, similar to YouTube but with additional social features. The project follows a standard Django MVT (Model-View-Template) architecture.

## Key Components

### Models (`app/models.py`)
- `Video`: Handles video uploads with automatic thumbnail generation using OpenCV
- `Post`: Supports text posts with optional images
- `VideoComment` & `PostComment`: Comment systems for both content types
- Key pattern: All content models include a `type` field for content differentiation

### Authentication System (`accounts/`)
- Custom user model implementation
- Integrated with Django's auth system
- Social features include user following system

### Media Handling
- Videos stored in `videos/` directory
- Thumbnails auto-generated in `thumbnail/` directory
- Post images stored in `postImages/` directory
- Supported video formats: mp4, mov, avi, wmv, flv, mkv, webm

## Development Workflows

### Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### Key Dependencies
- Django 5.2.6
- OpenCV (opencv-python) for thumbnail generation
- FFmpeg for video processing
- Markdown for text formatting

## Project Conventions

### Template Structure
- Base template: `app/templates/app/base.html`
- Template inheritance used throughout
- Content blocks: `title`, `heading`, `page_content`, `extra_navbar`

### URL Patterns
- Main routes in `app/urls.py`
- RESTful convention for content: `/watch/<id>` for videos, `/post/<id>` for posts
- API endpoints use hyphenated names (e.g., `like-video`, `follow-user`)

### Content Handling
1. Video uploads automatically generate thumbnails using OpenCV
2. Empty descriptions default to "There was no description provided for this video"
3. Media files accessed through Django's MEDIA_URL configuration

## Common Development Tasks

### Adding New Content Types
1. Create model in `app/models.py`
2. Add corresponding views in `app/views.py`
3. Create templates in `app/templates/app/`
4. Update URL patterns in `app/urls.py`

### Extending User Features
- User-related views handled in `accounts/views.py`
- Social features (following, likes) implemented through M2M relationships

## Integration Points
- OpenCV for video thumbnail generation
- FFmpeg for video processing
- Markdown for text formatting (see `markdown_extras.py` for custom extensions)