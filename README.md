# bonaso-data-viewer
Conceptual project creating a system for interacting with a database for my organization.

Planned Future Imporvements: 
    Better UI for filtering:
        Some fine tuning, but most of the basic functionality is there.
    
    APP: Send organization and get user information for requests and posts.
        The app needs to send information about the user requesting data when making requests to the server so that it knows what information to send. Really this is mostly for sending forms, but also for created_by for responses. 
        
    System for Batch Uploads:
        As either a supplement or alternative to file uploads based on forms, there should be a way for users to batch record a group of respondents and questions they were targeted with. 
        
    Improving File Uploads:
        File uploading for forms is a bit janky right now. There needs to be some more validation (checking logic, proper inputs, etc.) and there should also be a way for responses to be updated via files. Also, users need more information about when a field/respondent runs into an error so they can correct on their end. 

    Improving UI:
        Improve error messaging, directions, etc.


Important Notes:
Access Levels:
There are four acess levels. Data Collectors (only have the ability to create respondents, create and edit responses they created, and view forms), Supervisors(have the ability to create forms, view basic account information about their direct supervisees, view/edit responses), Managers (all supervisor's ability plus the ability to delete forms and view every member of the organization as well as members of child organizations) and Admins (who can basically do anything). 

Organizations:
By default, users will only be able to see content (forms, responses, etc.) related to their organization. Excepting Admins, who have the ability to view content for all organizations. 