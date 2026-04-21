import sys
import time
import traceback

from config import RSS_FEEDS, MAX_POSTS_PER_RUN
from rss_fetcher import fetch_feed, fetch_article_text
from translator import translate_article, format_fb_post
from facebook_poster import post_to_page
from storage import load_posted, mark_posted


def run(dry_run: bool = False) -> None:
    posted_ids = load_posted()
    published_count = 0

    print(f"[start] already posted: {len(posted_ids)} | limit: {MAX_POSTS_PER_RUN}")

    for feed in RSS_FEEDS:
        if published_count >= MAX_POSTS_PER_RUN:
            break

        print(f"\n[feed] {feed['name']}")
        try:
            items = fetch_feed(feed["url"], limit=5)
        except Exception as e:
            print(f"  feed error: {e}")
            continue

        for item in items:
            if published_count >= MAX_POSTS_PER_RUN:
                break

            article_id = item["id"]
            if not article_id or article_id in posted_ids:
                continue

            print(f"  -> {item['title'][:70]}")

            body = fetch_article_text(item["link"]) or item["summary"]
            if len(body) < 100:
                print("     skipped (too short)")
                continue

            try:
                translated = translate_article(
                    item["title"], body, feed["name"], item["link"]
                )
                post_text = format_fb_post(translated, feed["name"], item["link"])
            except Exception as e:
                print(f"     translate error: {e}")
                continue

            if dry_run:
                print("     [dry-run] would post:")
                print("     " + post_text.replace("\n", "\n     "))
            else:
                try:
                    res = post_to_page(post_text, link=item["link"])
                    print(f"     posted id={res.get('id')}")
                except Exception as e:
                    print(f"     fb error: {e}")
                    continue

            mark_posted(article_id)
            published_count += 1
            time.sleep(2)

    print(f"\n[done] published: {published_count}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    try:
        run(dry_run=dry)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
