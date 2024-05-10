'''
Copyright 2024 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Apr 03 2024
File : report_artifacts.py
'''
import logging
import report_artifacts_html

logger = logging.getLogger(__name__)

DEBUG = False

#--------------------------------------------------------------------------------#
def create_report_artifacts(reportData):
    logger.info("Entering create_report_artifacts")

    # Dict to hold the complete list of reports
    reports = {}

    if DEBUG:
        reportData["reportFileNameBase"] = "testing_report"
    htmlFile = report_artifacts_html.generate_html_report(reportData)
    
    reports["viewable"] = htmlFile
    reports["allFormats"] = [htmlFile]

    if DEBUG:
        import sys
        sys.exit()

    logger.info("Exiting create_report_artifacts")
    
    return reports 