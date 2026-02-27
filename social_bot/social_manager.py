#!/usr/bin/env python3
"""
NOVA SOCIAL MEDIA BOT - Auto-post to all platforms
Author: Rizwan Ali | Nova Global Keys
"""

import os
import sys
import json
import time
import random
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

sys.path.append('/srv/nova-global-keys')
from thor_engine import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/srv/nova-global-keys/logs/social_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('social-bot')

class SocialMediaBot:
    """Post to all platforms from one script"""
    
    def __init__(self):
        self.platforms = []
        self.posts_per_day = 15
        self.post_interval = 3600 / self.posts_per_day  # seconds between posts
        
        # Load platform configs
        self.load_platforms()
    
    def load_platforms(self):
        """Load API keys from config"""
        # LinkedIn
        if settings.LINKEDIN_TOKEN:
            self.platforms.append({
                'name': 'linkedin',
                'token': settings.LINKEDIN_TOKEN,
                'api_url': 'https://api.linkedin.com/v2/ugcPosts'
            })
        
        # Twitter/X
        if settings.TWITTER_BEARER_TOKEN:
            self.platforms.append({
                'name': 'twitter',
                'token': settings.TWITTER_BEARER_TOKEN,
                'api_url': 'https://api.twitter.com/2/tweets'
            })
        
        # Facebook
        if settings.FACEBOOK_PAGE_TOKEN:
            self.platforms.append({
                'name': 'facebook',
                'token': settings.FACEBOOK_PAGE_TOKEN,
                'api_url': f'https://graph.facebook.com/v18.0/{settings.FACEBOOK_PAGE_ID}/feed'
            })
        
        # Instagram Business
        if settings.INSTAGRAM_TOKEN:
            self.platforms.append({
                'name': 'instagram',
                'token': settings.INSTAGRAM_TOKEN,
                'api_url': f'https://graph.facebook.com/v18.0/{settings.INSTAGRAM_ID}/media'
            })
        
        # Telegram (you already have this)
        self.platforms.append({
            'name': 'telegram',
            'token': settings.TELEGRAM_TOKEN,
            'api_url': f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage'
        })
        
        logger.info(f"✅ Loaded {len(self.platforms)} platforms")
    
    def get_content_queue(self) -> List[Dict]:
        """Get posts to publish today"""
        # Option 1: From Google Sheets (via API)
        # Option 2: From local CSV
        # Option 3: AI-generated content
        
        # Example: Read from file
        try:
            with open('/srv/nova-global-keys/social_bot/content/posts.json', 'r') as f:
                return json.load(f)
        except:
            # Fallback - generate some posts
            return [
                {
                    'text': '📊 400 API calls/sec is not a flex. It\'s a requirement. #NovaGlobal #Bybit',
                    'image': None,
                    'time': '09:00'
                },
                {
                    'text': '🇵🇰 Built in Pakistan. Running global. Join the revolution. @Novaglobalkeysbot',
                    'image': None,
                    'time': '12:00'
                },
                {
                    'text': '🔔 FREE trading signals daily at @novaglobalsignals. RSI, MACD, Bollinger Bands.',
                    'image': None,
                    'time': '15:00'
                },
                {
                    'text': '💡 Level 3 Broker (Kr000820) means better fees, better execution, better results.',
                    'image': None,
                    'time': '18:00'
                },
                {
                    'text': '🚀 18 months of building. One complete ecosystem. Check GitHub: https://github.com/rizbot4u/nova-global-keys-',
                    'image': None,
                    'time': '21:00'
                }
            ]
    
    def post_to_linkedin(self, platform: Dict, content: str):
        """Post to LinkedIn"""
        headers = {
            'Authorization': f'Bearer {platform["token"]}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        data = {
            "author": f"urn:li:person:{settings.LINKEDIN_USER_ID}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(platform['api_url'], headers=headers, json=data)
            logger.info(f"LinkedIn post: {response.status_code}")
        except Exception as e:
            logger.error(f"LinkedIn error: {e}")
    
    def post_to_twitter(self, platform: Dict, content: str):
        """Post to Twitter/X"""
        headers = {
            'Authorization': f'Bearer {platform["token"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'text': content[:280]  # Twitter character limit
        }
        
        try:
            response = requests.post(platform['api_url'], headers=headers, json=data)
            logger.info(f"Twitter post: {response.status_code}")
        except Exception as e:
            logger.error(f"Twitter error: {e}")
    
    def post_to_facebook(self, platform: Dict, content: str):
        """Post to Facebook Page"""
        data = {
            'message': content,
            'access_token': platform['token']
        }
        
        try:
            response = requests.post(platform['api_url'], data=data)
            logger.info(f"Facebook post: {response.status_code}")
        except Exception as e:
            logger.error(f"Facebook error: {e}")
    
    def post_to_telegram(self, platform: Dict, content: str):
        """Post to Telegram channel (you already have this)"""
        data = {
            'chat_id': '@novaglobalsignals',  # or your main channel
            'text': content,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(platform['api_url'], json=data)
            logger.info(f"Telegram post: {response.status_code}")
        except Exception as e:
            logger.error(f"Telegram error: {e}")
    
    def post_to_all(self, content: str):
        """Post same content to all platforms"""
        for platform in self.platforms:
            if platform['name'] == 'linkedin':
                self.post_to_linkedin(platform, content)
            elif platform['name'] == 'twitter':
                self.post_to_twitter(platform, content)
            elif platform['name'] == 'facebook':
                self.post_to_facebook(platform, content)
            elif platform['name'] == 'telegram':
                self.post_to_telegram(platform, content)
            
            # Small delay between platforms
            time.sleep(2)
    
    def run_scheduler(self):
        """Main loop - posts at scheduled times"""
        logger.info(f"🚀 Social Bot started - {self.posts_per_day} posts/day")
        
        while True:
            now = datetime.now()
            content_queue = self.get_content_queue()
            
            for post in content_queue:
                # Parse scheduled time
                scheduled_time = datetime.strptime(post['time'], '%H:%M').time()
                scheduled_datetime = datetime.combine(now.date(), scheduled_time)
                
                # If time has passed today, schedule for tomorrow
                if scheduled_datetime < now:
                    scheduled_datetime += timedelta(days=1)
                
                # Wait until scheduled time
                wait_seconds = (scheduled_datetime - now).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"Next post at {scheduled_datetime.strftime('%H:%M')}")
                    time.sleep(min(wait_seconds, 60))  # Check every minute
                
                # Post it
                self.post_to_all(post['text'])
                
                # Wait random interval (10-30 min) to avoid pattern detection
                time.sleep(random.randint(600, 1800))
            
            # Sleep until next day
            tomorrow = now + timedelta(days=1)
            tomorrow_start = datetime.combine(tomorrow.date(), datetime.min.time())
            sleep_seconds = (tomorrow_start - datetime.now()).total_seconds()
            logger.info(f"Day complete. Sleeping until tomorrow")
            time.sleep(sleep_seconds)

if __name__ == "__main__":
    bot = SocialMediaBot()
    bot.run_scheduler()
