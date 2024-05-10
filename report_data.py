'''
Copyright 2024 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Apr 03 2024
File : report_data.py
'''
import logging

logger = logging.getLogger(__name__)
import common.api.project.project_users
import common.project_heirarchy
import users
import common.api.project.project_contact

#-------------------------------------------------------------------#
def gather_data_for_report(baseURL, authToken, reportData):
    logger.info("Entering gather_data_for_report")

    projectID = reportData["primaryProjectID"]
    reportOptions = reportData["reportOptions"]

    # Parse report options
    includeChildProjects = reportOptions["includeChildProjects"]

    projectList = common.project_heirarchy.create_project_heirarchy(baseURL, authToken, projectID, includeChildProjects)
    topLevelProjectName = projectList[0]["projectName"]
    # Get the list of parent/child projects start at the base project
    projectHierarchy = common.api.project.get_child_projects.get_child_projects_recursively(baseURL, projectID, authToken)

    reportData["topLevelProjectName"] = topLevelProjectName
    reportData["projectID"] = projectID
    reportData["projectList"] =projectList
    reportData["projectHierarchy"] = projectHierarchy

    projectResults = {}

    # Cycle through earch project and update user contacts and roles
    for project in projectList:
        
        projectName = project["projectName"]
        projectId = project["projectID"]
        
        projectResults[projectName] = {}

        print("        Managing users for project: %s" %projectName)

        contactUser = users.projectContact

        print("            Changing project contact to %s" %(contactUser))
        response = common.api.project.project_contact.update_project_contact(projectId, contactUser, baseURL, authToken)

        if "error" in response:
            if "message" in response["error"]:
                if "User does not have permission to perform this operation" in response["error"]:
                    print("            Current user does not have permission to change the project contact for this project")
                    projectResults[projectName]["Project Contact"]  = "Unchanged due to permissions"
                    continue
                else:
                    reportData["error"] = response["error"]
                    return reportData
        else:
            projectResults[projectName]["Project Contact"]  = "Updated to user : %s" %contactUser

        projectResults[projectName]["Project Contact"]

        # Now remove all users from the admin, analsyst and review roles that are not in the allowed user list
        for role in ["PROJECT_ADMIN", "ANALYST", "REVIEWER"]:
            usersToRemove = []
            usersToKeep = []

            projectResults[projectName][role] = {}
            projectResults[projectName][role]["removed"] = []
            projectResults[projectName][role]["added"] = []

            # Get the current users for this project and compare to the list of approved users
            response = common.api.project.project_users.get_project_users_by_role(projectID, role, baseURL, authToken)

            if "error" in response:
                reportData["error"] = response["error"]
                return reportData
            
            for user in response["data"]["users"]:
                if user not in users.allowedUsers:
                    usersToRemove.append(user)
                else:
                    usersToKeep.append(user)
             
            if len(usersToRemove):
                projectResults[projectName][role]["removed"] = usersToRemove
                
                # Now remove the list of users
                print("            Removing users from project role: %s " %role)
                response = common.api.project.project_users.remove_project_users_by_role(projectID, role, usersToRemove, baseURL, authToken)

                if "error" in response:
                    if "message" in response["error"]:
                        if "User does not have permission to perform this operation" in response["error"]:
                            print("            Current user does not have permission to change the project contact for this project")
                            continue
                        else:
                            reportData["error"] = response["error"]
                            return reportData
                
                print("                Users Removed: %s" %usersToRemove)
                projectResults[projectName][role]["Users removed"] = usersToRemove


            if len(users.allowedUsers):
                print("            Adding allowed users to project role: %s " %role)
                response = common.api.project.project_users.add_project_users_by_role(projectID, role, users.allowedUsers, baseURL, authToken)

                if "error" in response:
                    if "message" in response["error"]:
                        if "User does not have permission to perform this operation" in response["error"]:
                            print("            Current user does not have permission to change the project contact for this project")
                            continue
                        else:
                            reportData["error"] = response["error"]
                            return reportData


                print("                Users Added: %s" %users.allowedUsers)
                projectResults[projectName][role]["added"] = users.allowedUsers


    reportData["projectResults"]   = projectResults
          

    return reportData