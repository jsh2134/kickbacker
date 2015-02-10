Kickbacker
-----------
A web app built with Flask, Redis and Celery to incentivize your Kickstarter backers to spread the word. Your early backers are your biggest fans. They've already committed money, give them a reason to commit some time as well.

How it Works
--------------
Scrapes your Kickstarter project and its backers. Backers register and receive a link they can share across social media. Those who choose to participate compete against others in traffic and referrals to your project and are ranked on the page leaderboard. The winners receive additional prizes/rewards.

The App
---------
Runs on flask, stores data in redis, deploy to EC2 using fabric and boto, scrape with BeautifulSoup in the background via celery, keep it running with supervisor, store images in S3 and send mail with Mandrill

Make it Run
-------------
Install the requirements with pip. Create a secrets.py file in the root for services above. Update ec2.py config with your defaults and deploy to amazon.


