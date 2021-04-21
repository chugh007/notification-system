# Centralised Notification-system 

This system intends to create a centralised system which can send slack/email notification to any user in workspace using their email addresses .
The system services can be accessed via simple API calls, so it is easy to add anywhere in code and in ci/cd tools without depending on any plugins

Eg : 

```curl --location --request POST '<server dns name/ip>/post_on_slack?user=dummyuser@company.com&message=test'```

or 

```
curl --location --request POST '<server ip>/post_on_slack' \
--header 'Content-Type: application/json' \
--data-raw '{
    "user": "dummy@company.com",
    "message": "FOR BIG MESSAGES"
}'
```

System services include : 

      * Notification on Slack

            * HTTP CALL http://localhost/post_on_slack
            * Eg : params can be sent in  query string or in json body
            ```
                  curl --location --request POST 'localhost/post_on_slack' \
                  --header 'Content-Type: application/json' \
                  --data-raw '{
                  "user": "dummy@company.com",
                  "message": "FOR BIG MESSAGES"
                  }'
            ```

      * Notification on Email

            * HTTP CALL http://localhost/post_on_email 
            * Eg : params can be sent in  query string or in json body
                  ```
                  curl --location --request POST 'localhost/post_on_email' \
                  --header 'Content-Type: application/json' \
                  --data-raw '{
                  "user": "dummy@company.com",
                  "message": "FOR BIG MESSAGES"
                  }'
                  ```
            
      * Check status of Request

            * HTTP CALL http://localhost/check_status/<id recieved in above operation>
            * Eg: 
                  ```
                  curl --location --request GET 'localhost/check_status/607fe5228142d20de548412c' \
                  --header 'Content-Type: application/json' \
                  --data-raw '{
                  "user": "nikeshr@company.com",
                  "message": "*********2oi342o34o32"
                  }'
                  ```

## Deployment Instructions

### Mandatory softwares
      
      - docker
      - docker-compose

### Mandatory ENV VARS

      - SLACK_BOT_TOKEN 
      - MONGO_INITDB_ROOT_USERNAME
      - MONGO_INITDB_ROOT_PASSWORD
      - MONGO_INITDB_DATABASE
      - SMTP_SERVER
      - SMTP_PORT
      - SERVICE_EMAIL
      - SERVICE_PASSWORD

####  To generate SLACK_BOT_TOKEN ,first create an app and add to workspace https://youtu.be/Rufh3MjJz9g . Full tutorial to set up the app and generate the SLACK_BOT_TOKEN https://api.slack.com/tutorials/tracks/actionable-notifications .

### Architecture Diagram

![Alt text](notification_system.png?raw=true "Notification system")

### Execute the following code to start the server

Start the server by pulling images from docker hub
```
git clone https://github.com/chugh007/notification-system.git
cd notification-system
docker login #enter username and password 
docker-compose up #this will take pull from docker hub
```

Start the server by doing the build
```
git clone https://github.com/chugh007/notification-system.git
cd notification-system
docker login #enter username and password 
docker-compose up --build 
```



    