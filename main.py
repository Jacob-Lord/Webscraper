import requests
import webbrowser
from bs4 import BeautifulSoup
from tabulate import tabulate

def initialize_html(url):
    '''
    Returns the html data from url in string format 
    '''
    r = requests.get(url) #check site's response
    html = r.text
    return html


def create_html_file(file_name, html):
    '''
    Desc: Creates a .html file from html data
    '''
    file = open(file_name, "w")
    file.write(html)
    file.close()
    
def main():
    url = 'https://catalog.ucdenver.edu/cu-denver/undergraduate/courses-a-z/csci/' #url for program to scrape
    html = initialize_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    courses = soup.find_all("div", class_="courseblock")
    course_dict = {} #initialize dictionary to hold all future course entries
    course_list = []


    for course in courses:
        course_info = [] #store info from courses in a list format for tabulate later on
        #get course code
        course_code_html = course.find("span", class_="text col-3 detail-code margin--tiny text--huge")
        course_code = (course_code_html.text).rstrip(' -') #the .rstrip() fxn cuts off the space and dash at the end of the course code string
        course_info.append(course_code) #add course code to course_info list

        #get course title
        course_title_html = course.find("span", class_="text col-8 detail-title margin--tiny text--huge")
        course_title = course_title_html.text
        course_info.append(course_title) #add course title to course_info list

        #get course hours
        course_hours_html = course.find("span", class_="text detail-hours_html")
        course_hours = course_hours_html.text
        course_info.append(course_hours) #add course hours to course_info list

        #get courseblock extra information, desc and prereqs etc.
        #has multiple courseblocks that need to be iterated
        course_blocks = course.find_all("div", class_="noindent")
        #course_blocks = course_blocks_html.text

        course_prereqs = ""
        prereq = []
        for block in course_blocks: #iterate the different blocks in the course description
            if 'Prereq' in block.text: #find the prereq block
                prereqs = block.find_all("a", class_="bubblelink code") #list of prerequisites
                for x in prereqs: #iterate through the prereqs
                    #if x != block[len(block)-1]: #only add a comma if the prereq is not the last one in the block
                    if x.text in prereq:
                        break
                    
                    prereq.append(x.text) #add the prereq to the list of prereqs for this specific course

        pass_count = 1 #count number of iterations in for loop

        for string in prereq: #delete \xa0 substring from prereq course codes
            x = string.replace('\xa0', ' ')
            if pass_count < len(prereq): #if there is more than one prereq
                course_prereqs += string + ', '
            elif len(string) < 9: #there is a case where there is no CSCI prior to the course code as it is respectively implied, so insert CSCI (!specific to CSCI UCDenver page!)
                string = 'CSCI ' + string
                course_prereqs += string
            else: #last element or only element, don't add a comma
                course_prereqs += string

            pass_count += 1 #incrememnt pass_count

        course_info.append(course_prereqs) #add course prereqs to course_info list

        course_list.append(course_info) #add course_info list to the course_list to later be tabulated
                

    table_html = tabulate(course_list, tablefmt='html') #create html data from table data scraped and collected
    create_html_file('CS_courses.html', table_html) #create the html file from the data
    webbrowser.open_new_tab('CS_courses.html') #open the html file in the webbrowser for viewing






main()