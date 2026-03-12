# Welcome to my <a class='button'>YubTub</a> DEMO! {#top}

<style>
/* Mobile-responsive styles */
.video-grid {
    width: 100%;
    box-sizing: border-box;
}

.post-card {
    box-sizing: border-box;
}

.post-card iframe {
    width: 100%;
    height: auto;
    max-width: 575px;
    aspect-ratio: 575 / 750;
    pointer-events: none;
}

/* Tablet and up */
@media (min-width: 768px) {
    .video-grid {
        grid-template-columns: repeat(auto-fill, minmax(490px, 1fr)) !important;
    }
    
    .post-card iframe {
        width: 100%;
        height: auto;
        max-width: 575px;
        aspect-ratio: 575 / 750;
        pointer-events: none;
    }
}

/* Mobile optimization */
@media (max-width: 767px) {
    .video-grid {
        grid-template-columns: 1fr !important;
        padding: 0;
    }
    .post-card {
        width: 100%;
        padding: 10px;
    }
    .post-card iframe {
        max-width: 100%;
    }
}
</style>

<script>
</script>

## What *is* YubTub? {#what}

YubTub is a website built in python, running on my personal server.
It was origanily built as a Youtube clone, but has since evolved into more of a general social media website.

## What can you do on Yubtub? {#features}

- Posts
    - Use <abbr title="A lightweight, plain-text formatting language">markdown</abbr> to style post text
    - Mention other users with the @ symbol
    - Upload an image to go along with posts
        - (I am working on being able to upload multiple images)
    - Write comments
        - Which also can mention other users
- Videos
    - Use <abbr title="A lightweight, plain-text formatting language">markdown</abbr> to style video descriptions
    - Upload video files to be displayed on YubTub
    - Auto thumbnailing, so you dont have to upload thumbnails for your videos
    - Write comments
        - Which also can mention other users

## What do the forms look like?

<div class="video-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(490px, 1fr)); gap: 20px;">
    <div class="post-card">
        <iframe src="{% url 'app:makePost' %}"
        id="postIframe"
        frameborder="0"
        scrolling="yes"
        allow="camera; microphone"
        ></iframe>
    </div>
    <div class="post-card">
        <iframe src="{% url 'app:postVideo' %}"
        id="videoIframe"
        frameborder="0"
        scrolling="yes"
        allow="camera; microphone"
        ></iframe>
    </div>
</div>
