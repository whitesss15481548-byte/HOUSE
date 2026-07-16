
import argparse
import os
import json
import requests
from datetime import datetime

# Constants
FB_GRAPH_API_BASE = "https://graph.facebook.com/"
DEFAULT_GRAPH_API_VERSION = "v21.0"

# Helper function to mask token for display
def mask_token(token):
    if not token:
        return ""
    if len(token) <= 8:
        return "*" * len(token)
    return token[:4] + "*" * (len(token) - 8) + token[-4:]

# Load posted history
def load_posted_history():
    history_path = "repo/posted_history.json"
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save posted history
def save_posted_history(history):
    history_path = "repo/posted_history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Check if a post has already been published
def is_post_published(page, category, post_key, history):
    for record in history:
        if record["page"] == page and record["category"] == category and record["post_key"] == post_key and record["status"] == "published":
            return True
    return False

# Function to check configuration
def check_config():
    print("--- Configuration Check ---")
    page_id = os.environ.get("FB_PAGE_ID_HUANGYU")
    page_token = os.environ.get("FB_PAGE_TOKEN_HUANGYU")
    api_version = os.environ.get("FB_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION)

    print(f"FB_PAGE_ID_HUANGYU: {page_id if page_id else 'Not set'}")
    print(f"FB_PAGE_TOKEN_HUANGYU: {'Set' if page_token else 'Not set'}")
    print(f"FB_GRAPH_API_VERSION: {api_version}")
    print("---------------------------")

# Function to check token
def check_token(page_name):
    print(f"--- Token Check for {page_name} ---")
    page_token = os.environ.get(f"FB_PAGE_TOKEN_{page_name.upper()}")
    if page_token:
        print(f"FB_PAGE_TOKEN_{page_name.upper()}: {mask_token(page_token)}")
    else:
        print(f"FB_PAGE_TOKEN_{page_name.upper()}: Not set")
    print("---------------------------")

# Function to get the next post
def get_next_post(page, category, history):
    post_dir = os.path.join("repo", "posts", page, category)
    if not os.path.exists(post_dir):
        print(f"Warning: Post directory {post_dir} does not exist.")
        return None, None, None

    post_files = sorted([f for f in os.listdir(post_dir) if f.endswith(".txt")])

    for post_file in post_files:
        post_key = os.path.splitext(post_file)[0]
        if not is_post_published(page, category, post_key, history):
            text_path = os.path.join(post_dir, post_file)
            image_path = None
            for ext in [".png", ".jpg", ".jpeg"]:
                img_candidate = os.path.join(post_dir, post_key + ext)
                if os.path.exists(img_candidate):
                    image_path = img_candidate
                    break
            
            with open(text_path, "r", encoding="utf-8") as f:
                message = f.read()
            
            return post_key, message, image_path
    return None, None, None

# Function to publish post to Facebook
def publish_post(
    page_id, page_token, api_version, message, image_path=None, dry_run=True, page_name=None, category=None, post_key=None
):
    print(f"{'[DRY RUN] ' if dry_run else ''}Attempting to publish post...")
    
    if not page_id or not page_token:
        print("Error: Page ID or Page Token is not set.")
        return False

    url = f"{FB_GRAPH_API_BASE}{api_version}/{page_id}/photos" if image_path else f"{FB_GRAPH_API_BASE}{api_version}/{page_id}/feed"
    
    params = {
        "access_token": page_token,
        "message": message,
    }

    files = {}
    if image_path:
        try:
            files["source"] = open(image_path, "rb")
        except FileNotFoundError:
            print(f"Warning: Image file not found at {image_path}. Posting as text only.")
            image_path = None # Revert to text-only post
            url = f"{FB_GRAPH_API_BASE}{api_version}/{page_id}/feed"
            files = {}

    if dry_run:
        print("Dry run successful. No actual post was made.")
        print(f"Message: {message[:100]}...")
        if image_path:
            print(f"Image: {image_path}")
        return True

    try:
        if image_path:
            response = requests.post(url, params=params, files=files)
        else:
            response = requests.post(url, params=params)
        response.raise_for_status()
        post_id = response.json().get("id")
        print(f"Post published successfully! Post ID: {post_id}")
        
        # Record in history
        if page_name and category and post_key:
            history = load_posted_history()
            history.append({
                "page": page_name,
                "category": category,
                "post_key": post_key,
                "published_at": datetime.utcnow().isoformat() + "Z",
                "facebook_post_id": post_id,
                "status": "published",
            })
            save_posted_history(history)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error publishing post: {e}")
        if e.response:
            error_json = e.response.json()
            # Filter out token from error message
            if "access_token" in error_json.get("error", {}).get("message", ""): # Basic check, might need more robust filtering
                error_json["error"]["message"] = "[Token Redacted]"
            print(f"Facebook API Error: {json.dumps(error_json, ensure_ascii=False, indent=4)}")
        return False
    finally:
        if "source" in files and files["source"]:
            files["source"].close()

def main():
    parser = argparse.ArgumentParser(description="Facebook Auto Post System for Huangyu.")
    parser.add_argument("--check-config", action="store_true", help="Check current environment configurations.")
    parser.add_argument("--check-token", action="store_true", help="Check Facebook Page Token.")
    parser.add_argument("--page", type=str, help="Specify the Facebook page (e.g., huangyu).")
    parser.add_argument("--category", type=str, help="Specify the post category (e.g., saturday_money_class, sunday_cleanup).")
    parser.add_argument("--post", type=str, help="Specify a single post key (e.g., post_001) for testing.")
    parser.add_argument("--auto-next", action="store_true", help="Automatically find and publish the next unpublished post in the category.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actually publishing the post.")
    parser.add_argument("--publish", action="store_true", help="Publish the post to Facebook. Required for actual posting.")

    args = parser.parse_args()

    if args.check_config:
        check_config()
        return

    if args.check_token:
        if not args.page:
            print("Error: --page is required for --check-token.")
            return
        check_token(args.page)
        return

    if not args.page or not args.category:
        print("Error: --page and --category are required for posting actions.")
        return

    page_id = os.environ.get(f"FB_PAGE_ID_{args.page.upper()}")
    page_token = os.environ.get(f"FB_PAGE_TOKEN_{args.page.upper()}")
    api_version = os.environ.get("FB_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION)

    if not page_id or not page_token:
        print(f"Error: FB_PAGE_ID_{args.page.upper()} or FB_PAGE_TOKEN_{args.page.upper()} not found in environment variables.")
        return

    history = load_posted_history()

    post_key = None
    message = None
    image_path = None

    if args.post:
        post_key = args.post
        post_dir = os.path.join("repo", "posts", args.page, args.category)
        text_path = os.path.join(post_dir, post_key + ".txt")
        if not os.path.exists(text_path):
            print(f"Error: Specified post text file not found at {text_path}")
            return
        with open(text_path, "r", encoding="utf-8") as f:
            message = f.read()
        for ext in [".png", ".jpg", ".jpeg"]:
            img_candidate = os.path.join(post_dir, post_key + ext)
            if os.path.exists(img_candidate):
                image_path = img_candidate
                break
        if not image_path:
            print(f"Warning: No image found for post {post_key}. Posting as text only.")

    elif args.auto_next:
        post_key, message, image_path = get_next_post(args.page, args.category, history)
        if not post_key:
            print(f"目前沒有可發佈的新貼文在 {args.page}/{args.category}。")
            return
        if not image_path:
            print(f"Warning: No image found for post {post_key}. Posting as text only.")
    else:
        print("Error: Either --post or --auto-next must be specified for posting actions.")
        return

    if not message:
        print("Error: Post message is empty.")
        return

    if args.publish:
        publish_post(page_id, page_token, api_version, message, image_path, dry_run=False, page_name=args.page, category=args.category, post_key=post_key)
    elif args.dry_run:
        publish_post(page_id, page_token, api_version, message, image_path, dry_run=True)
    else:
        print("Error: Must specify either --publish or --dry-run for posting actions.")

if __name__ == "__main__":
    main()
