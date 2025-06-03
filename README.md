# bonaso-data-viewer
Conceptual project creating a system for interacting with a database for my organization.

Planned Future Imporvements: 
        APP: Send organization and get user information for requests and posts.
        The app needs to send information about the user requesting data when making requests to the server so that it knows what information to send. Really this is mostly for sending forms, but also for created_by for responses. 
   
    Improving File Uploads:
        File uploads work, but they're a bit limiting, need to figure out how to get user input for conflicts/updating records.

    Tutorial:
        Consider designing an information page.

    Need Redesign/Designs:
        Responses
        Login Page
        Home page


Important Notes:
Access Levels:
There are four acess levels. Data Collectors (only have the ability to create respondents, create and edit responses they created, and view forms), Supervisors(have the ability to create forms, view basic account information about their direct supervisees, view/edit responses), Managers (all supervisor's ability plus the ability to delete forms and view every member of the organization as well as members of child organizations) and Admins (who can basically do anything). 

Organizations:
By default, users will only be able to see content (forms, responses, etc.) related to their organization. Excepting Admins, who have the ability to view content for all organizations. 