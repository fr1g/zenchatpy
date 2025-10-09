# Routes Description

## Abstract

This project is a simple chatting project which can:

-   Add/CRUD people into contacts
-   Start chat with contact
-   Pull chat histories with pagination (on-scroll flush into client view)
-   Send/receive message

This one is pretty a simple one which in order to inspire ZenChatty App for diploma. :)

For Django Version: Only Private Chat, Only Basic Functions will be implemented. Full version, see: .NET version.

## REST-API Routes

These are basic APIs. Entry of these are under `/api`.

### Authentication and Authorization ... user related

-   `~/login`:  **POST** Token-free [JSON:UserLoginRequest] => UserCredential: Get required user's login info with a new valid token.
-   `~/logoff`: **POST** Token []: Vanish the given user token
-   `~/user/:uid?`: **POST** Token [path:uid?] => UserInfo: Returns a user's info without dangerous info (passwd etc.)
-   `~/refresh`: **POST** Token [] => UserCredential: Renew current user's JWT token and vanish the old one.
-   `~/register`: **PUT** Token-free [JSON:UserInfo] => UserCredential | null: Creates a new user and returns user's credentials (login by the time).
-   `~/update/:isUpdatePasswd?`: **UPDATE** Token [JSON:UserInfo; path: isUpdatePasswd?] => UserCredential: Update self-user-info and apply by re-login. If is admin, will also update admin's account.



### Admin Management

These are located under entry `~/admin`.

-   `~/get-all`: **POST** Token [string: keyword; int: page] => UserInfo[]: Get users by list, searched by keyword, pagination enabled.
-   `~/remove/:disable?`: **DELETE** Token [string: uid; path: disable? (bool)]: Remove or just disable the given user.
-   `~/update`: **UPDATE** Token [JSON:UserInfo]: Update anyone with anything, but cannot update password or uid.



### Message Related

These are located under entry `~/im`. These are related to IM functions. All of these requires a valid JWT Token.

-   `~/history`: **POST** [JSON:ChatHistoryRequest] => ChatHistory: using page-request info with a time period to get specified messages.
-   `~/detail/:msgSelector`: **POST** [path: msgSelector, boolean? thumbnail] => Message: passing a string message selector with format `chatId+msgUuid@senderUuid` to get a detailed message info, maybe for test only, or in order to download file. If required file is an image, and requiring as thumbnail, the returned Message.Content will be the base64 of compressed image. **[!!!]**
-   `~/file/:fileReference`: **GET** [path: fileReference] => FileStream: *Since each file - unless being forwarded - will only be shown in dedicated context of chat, so there's no security issues for users that CAN reach any file reference uuid.* Giving a fileReference UUID, returning a file stream of source file; or will return null if such file is not existing.
-   `~/msg-op/:msgSelector`: **POST** [path: msgSelector, JSON:MessageOperation]: Checks requester's permission, updates certain message, and send Announcement if needed.
-   `~/contact-events`: **GET** [] => ContactEvent[50?]: *only recent 50 events will be taken directly from server.* User's contact events notification: invited to group, added into group, removed from group, new-friend add, removed by friend, group issue, assigned or reassigned as admin of group. Possible user responses, see:
-   `~/ce-response/:accept`: **GET** [path: accept (boolean)]: Accept or not. If the original event is for notification only, the parameter `accept` can be any value.
-   



### Group Management Related

... basic CRUD for each group chats.



### Synchronically User Settings

... basic CRUD for user settings that able to be synchronized.  



### User Contact (People, Group) Info API

...



## WebSocket Routes

All WS Routes under `/ws` and requires JWT Token.

-   `~/msg/[group | private]/:chatid`: ~ [JSON:MessageInfo; path: chatid] => status (0~100): [[KEY MATTER]] Sending this format:

    `````json 
    {
        "type": "TXT" | "IMG" | "FILE",
        "content": "content or reference id of file (double-uuid)",
        "sendTime": timestamp (long),
        "original": "original content (text)",
        "status": editedAt(edit time) | "removedBy(remover uuid)",
        "mentioned": [list Users]
    }
    `````

    can get a status code that refers whether the server received and secured the message.
    The WS socket sends this kind of packet as a message (may compressed / ellipsis):

    `````json
    {
        "type": "TXT" | "IMG" | "FILE",
        "content": "content or reference id of file (double-uuid)",
        "sendTime": timestamp (long),
        "status": editedAt(edit time) | "removedBy(remover uuid)",
        "mentioned": [list Users],
        "original": null (type: text | file) | "IMG Base64 Thumbnail" 
    }
    `````

    History message can be get via POST request `/api/im/history`

    

-   `~/msg/ann`: ~ [] => Announcement: Important status updater, which includes many different types: MsgExceptionAnnouncement, GroupEventAnnouncement, MentionAnnouncement, SecurityAnnouncement, ContactAnnouncement

    -   MsgExceptionAnnouncement: If any message met exception when server is processing it, returning it can let client announce user to retry sending, and leave a reload button by the message. This will be removed after user clicked retry or deleted on client.
    -   GroupEventAnnouncement: When admin or owner of group removed user's message, or removed user from group, or muted user, client will catch this event.
    -   MentionAnnouncement: When another user in single chat used mention or any user in group mentioned all users / mentioned client user, or a group released a new notification, user will get a mention announce. The chat will be highlighted in client view.
    -   SecurityAnnouncement: Will announce user if some Security issue happened. Like: Force Offline, Offline
    -   ContactAnnouncement: Announces user, if contact got changed, like: invited to group, added into group, removed from group, new-friend add, removed by friend, group issue, assigned or reassigned as admin of group

-   

Client-removed message will be hidden on this client - removed by selector ID (chatId+msgUuid)



\# if DJANGO

## Template View Routes

-   `/:@uuid`: Home view (chat app), uuid: selected chatting user's uuid.
-   `/contacts`: detailed contacts list (paged)
-   `/about`: about page



\# elif DOTNET

## Additional Info

-   Implement of Offline Chatting should be like: On the MOBILE side, network-free, using latest user profile to start an on-bluetooth server, receiving connections-in, and it mostly like a broadcast room: members IN ROOM will receive EVERY MESSAGES inside, creator CAN BAN ANYONE, EVERYONE have 3s freeze time until next round to send, each room can only connect 9 members (including creator will be 10 members)



\# endif