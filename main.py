import requests
import webbrowser
from bs4 import BeautifulSoup
from tabulate import tabulate
import networkx as nx # Referenece: Tutorial — NetworkX 3.2.1 documentation
import matplotlib.pyplot as plt 

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

def display_html(html_file):
    '''
    Desc: Displays a html file in a web browser launched by this function
    '''
    webbrowser.open_new_tab(html_file)

def create_graph(course_list):
    '''
    Desc: Creates a network graph of courses and their prerequisites from a list of lists containing course informtation.
    '''
    #create a graph object
    G = nx.DiGraph()

    #add nodes to graph
    for x in course_list:
        G.add_node(x[0])

    #add edges
    for x in course_list:
            if len(x[3]) > 9: #if there if more than 1 prereq, so split string of prereqs into a real list that can be iterated
                prereq_list = x[3].split(', ')
                for _ in prereq_list: 
                    G.add_edge(x[0], _) #draw edge from course to its prereq
            elif len(x[3]) > 0:
                G.add_edge(x[0], x[3]) #draw edge from course to prereq if there is only 1
    
    # Create a graph
    plt.subplots(figsize=(25,25))
    pos = nx.random_layout(G)  # Positioning of nodes

    # Draw the graph
    nx.draw(G, pos, with_labels=True, font_size=4.5, font_weight='bold', node_color="#009999", node_size=350, arrowsize=5, width=0.5) #hopefully nobody seeing this is colorblind

    nx.draw_networkx_edges(G, pos, width=0.5, arrowsize=5, node_size= 350, edge_color='#774B4B')

    # Show the graph
    plt.axis('on')
    plt.show()

def scrape_courses_info(courses):
    '''
    Desc: Scrapes the course information from the CS crouse list html
    '''
    course_list = [] #holds course entries
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
            string = string.replace('\xa0', ' ')
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

    return course_list #return list containing list of courses and their respective info
    
def scrape_UCD():
    '''
    Desc: Scrapes the CU Denver CS course catalog for information and returns the data as a table in a .html file.
    Returns a string of the .html's file name
    '''
    url = 'https://catalog.ucdenver.edu/cu-denver/undergraduate/courses-a-z/csci/' #url for program to scrape
    html = initialize_html(url) #get html from webpage
    soup = BeautifulSoup(html, 'html.parser') #initialize parser
    courses = soup.find_all("div", class_="courseblock") #get course html from webpage html
    course_list = scrape_courses_info(courses) #scrape course info from courses html and return them as a list of lists of course info
    table_html = tabulate(course_list, tablefmt='html') #create html data from table data scraped and collected
    html_filename = 'CS_courses.html'
    create_html_file(html_filename, table_html) #create the html file from the data
    create_graph(course_list) #create network of courses and prereqs
    return html_filename

def scrape_COVID_data():
    '''
    Desc: Scrapes the CO Covid-19 official metrics page for the metric data and returns it as a table in a .html file.
    Returns a string of the .html's file name
    '''
    url = "https://cdphe.colorado.gov/covid-19/data"
    html = initialize_html(url)
    soup = BeautifulSoup(html, 'html.parser') #initialize parser
    covid_table = soup.find("table", attrs={'dir':'ltr'}) #gather covid table from html data

    table = [] #list of lists of table rows which will be turned into html
    row_count = 0 #display row number in table
    table_rows = (covid_table.find("tbody")).find_all("tr")
    for row in table_rows: #for each row in the table
        table_row_data = [] #initialize table_row_data as empty
        table_row_data.append(row_count) #add row number to front of row
        row_data = row.find_all("td") #extract the cells from the row
        for data in row_data: #extract the data from the cells
            table_row_data.append(data.text) #append the text data to table_row_data 
        table.append(table_row_data) #add row to table list
        row_count += 1
    
    table_html = tabulate(table, tablefmt='html') #create an html table using tabulate method from import
    html_filename = 'COVID_County_Data_CO.html'
    create_html_file(html_filename, table_html) #generate html file from the html data
    return html_filename

def main():
    #UCD Scrape
    html = scrape_UCD()
    display_html(html)

    #CO COVID-19 Metric Scrape
    html = scrape_COVID_data()
    display_html(html)

main()