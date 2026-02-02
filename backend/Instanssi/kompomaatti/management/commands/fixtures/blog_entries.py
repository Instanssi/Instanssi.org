"""Test blog entries for events"""

from datetime import UTC, datetime

blog_entries = [
    # Blog entries for Instanssi 2026 (upcoming event) - Many entries for pagination testing
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Instanssi 2026 - Registration Open!",
        "text": """<p>We are excited to announce that registration for Instanssi 2026 is now open!</p>
<p>Join us February 26-28, 2026 for another amazing event featuring:</p>
<ul>
<li>Graphics, Music, and Demo competitions</li>
<li>Speed Coding and Speedrun challenges</li>
<li>Live streaming and voting</li>
<li>Community hangout and networking</li>
</ul>
<p>Visit the registration page to sign up now. Early bird tickets available!</p>""",
        "date": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Compo Schedule Released",
        "text": """<p>The complete schedule for Instanssi 2026 compos is now available!</p>
<p><strong>Friday, February 27:</strong></p>
<ul>
<li>18:00 - Graphics compo</li>
<li>19:00 - Music compo</li>
<li>20:00 - Demo compo</li>
</ul>
<p><strong>Saturday, February 28:</strong></p>
<ul>
<li>14:00 - Speed Coding competition</li>
<li>14:00 - Speedrun Challenge</li>
</ul>
<p>Entry submissions close February 22, so get your work ready!</p>""",
        "date": datetime(2026, 2, 1, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Draft: Venue Details",
        "text": """<p>This is a draft blog entry with venue information.</p>
<p>Will be published closer to the event date.</p>""",
        "date": datetime(2026, 2, 10, 15, 0, 0, tzinfo=UTC),
        "public": False,  # Draft entry
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Sponsor Announcement: TechCorp Finland",
        "text": """<p>We are thrilled to announce that TechCorp Finland has joined as a Gold sponsor!</p>
<p>Their generous support helps us make Instanssi even better. Thank you!</p>""",
        "date": datetime(2026, 1, 20, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "New Compo Category: Shader Showdown",
        "text": """<p>This year we're introducing a new compo: Shader Showdown!</p>
<p>Create stunning visual effects using GLSL shaders. Max 4KB size limit.</p>""",
        "date": datetime(2026, 1, 22, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Accommodation Info",
        "text": """<p>Looking for a place to stay during Instanssi 2026?</p>
<p>We've partnered with local hotels for discounted rates. Use code INST2026.</p>""",
        "date": datetime(2026, 1, 25, 11, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Volunteer Call",
        "text": """<p>Want to help out at Instanssi 2026? We need volunteers!</p>
<p>Help with setup, registration desk, or compo organization. Free entry included!</p>""",
        "date": datetime(2026, 1, 28, 16, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Music Compo Rules Update",
        "text": """<p>Important update to music compo rules:</p>
<p>Maximum track length increased to 5 minutes. Streaming format now required.</p>""",
        "date": datetime(2026, 2, 3, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Live Stream Information",
        "text": """<p>Instanssi 2026 will be streamed live on multiple platforms!</p>
<p>Twitch, YouTube, and our own website. Links will be posted before the event.</p>""",
        "date": datetime(2026, 2, 5, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Demo Compo Technical Requirements",
        "text": """<p>Technical requirements for demo compo entries:</p>
<p>Windows 10/11, DirectX 12 or OpenGL 4.6. Max runtime: 8 minutes.</p>""",
        "date": datetime(2026, 2, 7, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Prize Pool Announced!",
        "text": """<p>Total prize pool for Instanssi 2026: 5000 EUR!</p>
<p>Thanks to our sponsors for making this possible. Good luck to all participants!</p>""",
        "date": datetime(2026, 2, 8, 11, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Graphics Compo Theme Revealed",
        "text": """<p>The optional theme for this year's graphics compo is: "Retro Future"</p>
<p>Combine vintage aesthetics with futuristic elements. Theme is optional but encouraged!</p>""",
        "date": datetime(2026, 2, 9, 15, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Food and Drinks at the Venue",
        "text": """<p>Information about food options at Instanssi 2026:</p>
<p>Cafeteria on-site, pizza delivery available, free coffee for all attendees!</p>""",
        "date": datetime(2026, 2, 11, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Network Setup Complete",
        "text": """<p>Our network team has completed the setup!</p>
<p>1Gbps wired connections available, plus stable WiFi throughout the venue.</p>""",
        "date": datetime(2026, 2, 12, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Seminars and Talks Schedule",
        "text": """<p>We have amazing seminars lined up!</p>
<p>Topics include: shader optimization, music production, and demoscene history.</p>""",
        "date": datetime(2026, 2, 13, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Speedrun Competition Details",
        "text": """<p>Speedrun competition game announced: Classic Doom!</p>
<p>Any% category, real-time timing. Prizes for top 3 finishers.</p>""",
        "date": datetime(2026, 2, 14, 11, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Draft: After Party Plans",
        "text": """<p>Draft post about the after party. Details TBD.</p>
<p>Location and time to be announced.</p>""",
        "date": datetime(2026, 2, 14, 16, 0, 0, tzinfo=UTC),
        "public": False,  # Draft
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Entry Submission Deadline Reminder",
        "text": """<p>Reminder: Entry submissions close on February 22!</p>
<p>Don't wait until the last minute. Upload your entries now.</p>""",
        "date": datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Wild Compo Open",
        "text": """<p>The Wild Compo is now accepting entries!</p>
<p>Anything goes: hardware demos, animations, games, art installations.</p>""",
        "date": datetime(2026, 2, 16, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Voting System Test",
        "text": """<p>We're testing the voting system this weekend.</p>
<p>If you have a ticket, you can test vote on some sample entries.</p>""",
        "date": datetime(2026, 2, 17, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Community Meet-up Before Event",
        "text": """<p>Join us for an informal meet-up on Thursday evening!</p>
<p>Great opportunity to meet fellow sceners before the main event starts.</p>""",
        "date": datetime(2026, 2, 18, 11, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Parking Information",
        "text": """<p>Parking available at the venue!</p>
<p>Free parking in the main lot. Overnight parking allowed for ticket holders.</p>""",
        "date": datetime(2026, 2, 19, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Quiet Room Available",
        "text": """<p>We have a quiet room for attendees who need a break.</p>
<p>Located on the second floor. Please respect others using this space.</p>""",
        "date": datetime(2026, 2, 20, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Last Minute Entry Tips",
        "text": """<p>Still working on your entry? Here are some last-minute tips:</p>
<p>Test on clean system, include readme, check file size limits!</p>""",
        "date": datetime(2026, 2, 21, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Submissions Closing Soon!",
        "text": """<p>Only 24 hours left to submit your entries!</p>
<p>Deadline: February 22, 23:59 UTC. No extensions!</p>""",
        "date": datetime(2026, 2, 21, 23, 59, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 25,
        "user_username": "admin",
        "title": "Draft: Results Preview",
        "text": """<p>Internal draft for results announcement.</p>
<p>DO NOT PUBLISH - contains preliminary scores.</p>""",
        "date": datetime(2026, 2, 22, 12, 0, 0, tzinfo=UTC),
        "public": False,  # Draft
    },
    # Blog entries for Instanssi 2024 (archived event)
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Instanssi 2024 - Thank You!",
        "text": """<p>Instanssi 2024 is now over! Thank you to everyone who participated.</p>
<p>We had amazing entries in all categories and great turnout for the competitions.</p>
<p>Results are now available in the archive. Congratulations to all winners!</p>
<p>See you next year!</p>""",
        "date": datetime(2024, 3, 2, 18, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Final Day - Voting Closes Soon",
        "text": """<p>Today is the final day of Instanssi 2024!</p>
<p>Voting closes at 12:00 today. Make sure to cast your votes for your favorite entries.</p>
<p>Results will be announced this evening. Stay tuned!</p>""",
        "date": datetime(2024, 3, 2, 9, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Instanssi 2024 Kicks Off!",
        "text": """<p>Instanssi 2024 has officially started!</p>
<p>Compos begin tonight. Graphics compo at 18:00, Music at 19:00.</p>
<p>Live stream is available on our website. Don't miss it!</p>""",
        "date": datetime(2024, 3, 1, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Pre-party Tonight!",
        "text": """<p>Join us for the pre-party tonight at 20:00!</p>
<p>Drinks, snacks, and good company. See you there!</p>""",
        "date": datetime(2024, 2, 29, 15, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 23,
        "user_username": "admin",
        "title": "Registration Now Open for 2024",
        "text": """<p>Instanssi 2024 registration is now open!</p>
<p>Early bird tickets available until February 15.</p>""",
        "date": datetime(2024, 1, 10, 12, 0, 0, tzinfo=UTC),
        "public": True,
    },
    # Blog entries for Instanssi 2023
    {
        "event_pk": 22,
        "user_username": "admin",
        "title": "Instanssi 2023 - Thanks for Coming!",
        "text": """<p>Another successful Instanssi is in the books!</p>
<p>We had record participation this year with amazing demos, graphics, and music entries.</p>
<p>All results are now published in the archive section.</p>
<p>Special thanks to our sponsors and volunteers who made this possible!</p>""",
        "date": datetime(2023, 3, 5, 20, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 22,
        "user_username": "admin",
        "title": "Welcome to Instanssi 2023",
        "text": """<p>Instanssi 2023 is here! Welcome to all attendees.</p>
<p>Check out the schedule and don't forget to vote after watching the compo entries.</p>
<p>Have a great time!</p>""",
        "date": datetime(2023, 3, 3, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 22,
        "user_username": "admin",
        "title": "Instanssi 2023 Schedule Posted",
        "text": """<p>The full schedule for Instanssi 2023 is now available!</p>
<p>Check the programme page for all the details.</p>""",
        "date": datetime(2023, 2, 20, 14, 0, 0, tzinfo=UTC),
        "public": True,
    },
    # Blog entries for Instanssi 2021
    {
        "event_pk": 19,
        "user_username": "admin",
        "title": "Instanssi 2021 Wrap-Up",
        "text": """<p>What an amazing event! Instanssi 2021 was a huge success.</p>
<p>Thanks to everyone who submitted entries and participated in voting.</p>
<p>See the archive for full results and all the incredible entries we received.</p>""",
        "date": datetime(2021, 3, 7, 16, 0, 0, tzinfo=UTC),
        "public": True,
    },
    {
        "event_pk": 19,
        "user_username": "admin",
        "title": "Online Event This Year",
        "text": """<p>Due to the global situation, Instanssi 2021 will be held online.</p>
<p>All compos and voting will happen remotely. Stay tuned for details!</p>""",
        "date": datetime(2021, 2, 1, 10, 0, 0, tzinfo=UTC),
        "public": True,
    },
]
