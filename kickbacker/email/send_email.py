import mandrill

from secrets import MANDRILL
from email import config

m = mandrill.Mandrill(MANDRILL)

template = config.templates['new_kb']

vals = {
    "template_name": template['name'],
    "template_content": [
        {
            "name": "example name",
            "content": "example content"
        }
    ],
    "message": {
        "subject": "example subject",
        "from_email": config.account_info['from_email'],
        "from_name": config.account_info['from_name'],
        "to": [
            {
                "email": "jsh2134+heynow@gmail.com",
                "name": "Hey Now"
            }
        ],
        "headers": {
            "Reply-To": "message.reply@example.com"
        },
        "track_opens": None,
        "track_clicks": None,
        "auto_text": None,
        "auto_html": None,
        "inline_css": None,
        "url_strip_qs": None,
        "preserve_recipients": None,
        "bcc_address": "message.bcc_address@example.com",
        "tracking_domain": None,
        "signing_domain": None,
        "merge": True,
        "global_merge_vars": [
            {
                "name": "merge1",
                "content": "merge1 content"
            }
        ],
        "merge_vars": [
            {
                "rcpt": "recipient.email@example.com",
                "vars": [
                    {
                        "name": "merge2",
                        "content": "merge2 content"
                    }
                ]
            }
        ],
        "tags": [
            "password-resets"
        ],
        "google_analytics_domains": [
            "example.com"
        ],
        "google_analytics_campaign": "message.from_email@example.com",
        "metadata": {
            "website": "www.example.com"
        },
        "recipient_metadata": [
            {
                "rcpt": "recipient.email@example.com",
                "values": {
                    "user_id": 123456
                }
            }
        ],
        "attachments": [
            {
                "type": "text/plain",
                "name": "myfile.txt",
                "content": "ZXhhbXBsZSBmaWxl"
            }
        ],
        "images": [
            {
                "type": "image/png",
                "name": "IMAGECID",
                "content": "ZXhhbXBsZSBmaWxl"
            }
        ]
    },
    "async": False
}



print m.messages.send_template(**vals)
