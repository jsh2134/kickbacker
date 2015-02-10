Kickbacker
-----------
A web app built with Flask, Redis and Celery to incentivize your Kickstarter backers to spread the word. Scrapes your Kickstarter project and its backers.

Backers register and receive a link they can share across social media. Those who choose to participate compete against others in traffic and referrals to your project and are ranked on the page leaderboard. The winners receive additional prizes/rewards.

Deployment to EC2 using fabric and boto, scrape with BeautifulSoup in the background with celery, keep it running with supervisor and send mail with Mandrill
