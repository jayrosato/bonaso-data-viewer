# bonaso-data-viewer
Conceptual project creating a system for interacting with a database for my organization.

Planned Future Imporvements:
    System for Batch Uplaods:
        As either a supplement or alternative to file uploads based on forms, there should be a way for users to batch record a group of respondents and questions they were targeted with. 
        
    Improving File Uploads:
        File uploading for forms is a bit janky right now. There needs to be some more validation (checking logic, proper inputs, etc.) and there should also be a way for responses to be updated via files. Also, users need more information about when a field/respondent runs into an error so they can correct on their end. 
    
    Better UI for filtering:
        This site is theoretically supposed to manage quite a few people, so at some point, the numberor forms/questions/responses/options is going to get out of hand. There needs to be some kind of filtering/search funcitonality for a lot of the select options, and probably also something like filters and page navigators for using indexes. 

    Better data validity checks/error handling:
        There is some basic funcitonality here already, but still quite a few ways a user could accidently create an error. Also, the few validity checks that exist have poor messaging. 


Important Notes:
Access Levels:
There are four acess levels. Data Collectors (only have the ability to create respondents, create and edit responses they created, and view forms), Supervisors(have the ability to create forms, view basic account information about their direct supervisees, view/edit responses), Managers (all supervisor's ability plus the ability to delete forms and view every member of the organization as well as members of child organizations) and Admins (who can basically do anything). 

Organizations:
By default, users will only be able to see content (forms, responses, etc.) related to their organization. Excepting Admins, who have the ability to view content for all organizations. 