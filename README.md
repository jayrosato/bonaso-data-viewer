# bonaso-data-viewer
Conceptual project creating a system for interacting with a database for my organization.

Planned Future Imporvements:
    System for Batch Uplaods:
        As either a supplement or alternative to file uploads based on forms, there should be a way for users to batch record a group of respondents and questions they were targeted with. 
        
    Improving File Uploads:
        File uploading for forms is a bit janky right now. There needs to be some more validation (checking logic, proper inputs, etc.) and there should also be a way for responses to be updated via files. Also, users need more information about when a field/respondent runs into an error so they can correct on their end. 
    
    Better UI for filtering:
        Search bars for selects are functional, but not very ui friendly, and 100% need to be worked on. Also, some of the filters for tables need to be redone slightly.

    Better data validity checks/error handling:
        Data validity is basically funcitonal, but there needs to be better messaging. Also, we need to determine a way to record an absence of data (i.e., none).


Important Notes:
Access Levels:
There are four acess levels. Data Collectors (only have the ability to create respondents, create and edit responses they created, and view forms), Supervisors(have the ability to create forms, view basic account information about their direct supervisees, view/edit responses), Managers (all supervisor's ability plus the ability to delete forms and view every member of the organization as well as members of child organizations) and Admins (who can basically do anything). 

Organizations:
By default, users will only be able to see content (forms, responses, etc.) related to their organization. Excepting Admins, who have the ability to view content for all organizations. 