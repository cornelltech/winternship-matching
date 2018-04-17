import csv
import os
import pdb

from enum import Enum

INTERESTS = ['Artificial Intelligence', 'Data Analytics', 'Design/Branding',
        'eCommerce', 'Ed Tech', 'Fin Tech', 'Fashion Tech', 'Health Tech',
        'Hardware', 'Human Resources', 'Internet of Things', 'Law', 'Mobile',
        'Media', 'Security and Privacy', 'Social Entrepreneurship', 'Social Media',
        'Software Development', 'Virtual Reality']

def read_file(filename):
    contents = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contents.append(row)
    return contents

def get_interests(entity):
    keys = INTERESTS

    interests, other = [], None
    for key in keys:
        if entity[key] == key:
            interests.append(entity[key])
    if entity['Other']:
        other = entity['Other']
    return (interests, other)

def get_company_timeline(company):
    timeline = company['What is your Winternship timeline?The Winternship program is two or three weeks during the winter...']
    if timeline == 'We want to participate for three weeks from Jan 8-26':
        return 'Jan 8-26'
    elif timeline == 'We want to participate for the first two weeks from Jan 8-19':
        return 'Jan 8-19'
    elif timeline == 'We want to participate for the last two weeks from Jan 15-26':
        return 'Jan 15-26'
    else:
        return timeline

def get_number_of_winterns(company):
    return int(company['# of Winterns'])

def get_company_profile(company):
    profile = {}
    interests, other = get_interests(company)
    size = company['Size']
    timeline = get_company_timeline(company)
    number = get_number_of_winterns(company)

    profile['name'] = company['Company Name']
    profile['interests'] = interests
    profile['size'] = size
    profile['timeline'] = timeline
    profile['number'] = number
    profile['location'] = company['Primary Company Location']
    
    return profile
    # return profile['name'], profile

# TODO: how to handle this? rly complicated for now
def get_grad_year(student):
    return student['Your anticipated graduation date (year)']

def get_size_preference(student):
    pref = student['Do you have a preference for working in a small, medium, or large sized company? And why?']
    # TODO: search thru for coherent size preferences somehow
    return pref

def yesno_to_tf(student, field):
    return (student[field].lower() == 'yes')

def get_student_timeline(student):
    timeline = student['When are you available? ']
    if timeline == 'I am available all three weeks from Jan 8-26':
        return 'Jan 8-26'
    elif timeline == 'I am available the first two weeks from Jan 8-19':
        return 'Jan 8-19'
    elif timeline == 'I am available the last two weeks from Jan 15-26':
        return 'Jan 15-26'
    else:
        return timeline

def get_student_profile(student):
    profile = {}
    interests, other = get_interests(student)
    size = get_size_preference(student)

    profile['email'] = student['Contact Info-Email']
    profile['gender'] = student['Your Gender\xa0Identity']
    profile['interests'] = interests
    profile['size'] = size
    profile['computer'] = yesno_to_tf(student, 'computer')
    profile['Macaulay'] = yesno_to_tf(student, 'Macaulay')
    profile['Guild'] = yesno_to_tf(student,'Guild')
    profile['Legal'] = yesno_to_tf(student, 'Legal')
    profile['school'] = student['Your CUNY School']
    profile['travel'] = yesno_to_tf(student, 'travel\xa0')
    profile['class'] = student['Your Class Year']
    profile['graduation'] = get_grad_year(student)
    profile['timeline'] = get_student_timeline(student)

    # short answers
    passionate = student['What are you passionate about?']
    goals = student['What are your goals for participating in the Winternship Program? \xa0']
    learn = student['What do you hope to learn from the Winternship experience?']
    career = student['What activities and experiences demonstrate your interest in a tech career?']
    team = student['Tell us what experience you’ve had working on a team and how you would describe yourself as part...']
    whyme = student['Why should you be picked to participate in the Winternship Program?']

    profile['short_answers'] = [passionate, goals, learn, career, team, whyme]

    return profile

class Match(Enum):
    BEST = 1
    GOOD = 2
    OK = 3
    NO = 4
    ANY = 5

def interests_match(student_interests, company_interests):
    if student_interests == INTERESTS:
        return Match.ANY
    elif student_interests == company_interests:
        return Match.BEST # they're interested in exactly the same stuff
    elif company_interests and set(company_interests).issubset(student_interests):
        return Match.GOOD # student is interested in all of company's interests
    elif [val for val in company_interests if val in student_interests]:
        return Match.NO # they have no interests in common
    else:
        return Match.OK # there is some overlap


def student_company_match(student_p, company_p):
    location_match = student_p['travel'] or (company_p['location'] == 'NYC')
    schedule_match = (student_p['timeline'] == company_p['timeline'])
    if location_match and schedule_match:
        return interests_match(student_p['interests'], company_p['interests'])
    else:
        return Match.NO

def short_answers_ok(answers):
    for ans in answers:
        if len(ans) < 10:
            return False
    return True

def student_ok(student_profile):
    return student_profile['Legal'] and \
        short_answers_ok(student_profile['short_answers']) and \
        student_profile['gender'] != 'Male'

# TODO: add a reason to bad students...
def separate_bad_students(student_profiles):
    good, bad = [], []
    for student_profile in student_profiles:
        if student_ok(student_profile):
            good.append(student_profile)
        else:
            bad.append(student_profile)
    return good, bad

if __name__ == '__main__':
    students = read_file('students.csv')
    companies = read_file('companies.csv')

    s_data = {student['Contact Info-Email']: student for student in students}

    student_profiles = [get_student_profile(student) for student in students]
    good_students, bad_students = separate_bad_students(student_profiles)
    company_profiles = [get_company_profile(company) for company in companies]

    print (len(student_profiles))
    print(len(good_students))
    print(len(bad_students))
    print (len(company_profiles))
    for student_profile in good_students:
        for company_profile in company_profiles:
            email = student_profile['email']
            # print (email)
            match = student_company_match(student_profile, company_profile)
            s_data[email][company_profile['name']] = match.name

    # TODO: get this data more consistently
    headers = list(s_data['Juaritzel.11@gmail.com'].keys())
    with open('matches.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()
        for student in good_students:
            email = student['email']
            print(email)
            writer.writerow(s_data[email])
    
            # print(list(s_data[email].keys()))

    # print(get_company_profile(companies[0]))
    # print()
    # print(get_student_profile(students[0]))
