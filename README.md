# Music Hosting Platform

## Full-stack application simulating a music hosting platform for both artist and listener users integrated with a MySQL database.

This is my capstone project for Purdue's CS348 (Information Systems & Databases) course in the department of Computer Science. Project development was individual and lasted for the entire semester.

The particular emphasis of this project was to integrate a relational database within a web/mobile application, utilizing key concepts touched on in class (database design, database queries in code, transactions and concurrency). In my case, I used a MySQL database hosted with a frontend interface utilizing FastAPI in the backend.

We were given complete creative control over the context of the application. My application mimics a music hosting platform, where artists are able to add albums and tracks to the central database, which is also accessible to listeners who can add such tracks to their custom playlists.

## Demo Video

Be sure to check out the full [demo video](https://youtu.be/FVRNfCCP-qc) that I used as my final project submission.

## Future Areas of Improvement

Some areas for improvement within this project (as touched on in the demo video) include...

• Improved dynamic integration of user input into html values (Jinja2).
• Implementing a refresh timer so that table values are periodically updated in cases of multiple users.
• Possibly integrate a NoSQL database for scalability.