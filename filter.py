import csv
import operator
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

    interests = []
    for key in keys:
        if entity[key] == key:
            interests.append(entity[key])
    return interests

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
    interests = get_interests(company)
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
    return student['Graduation']

def yesno_to_tf(student, field):
    return (student[field].lower() == 'yes')

def get_student_timeline(student):
    timeline = student['When']
    if timeline == 'I am available all three weeks from Jan 8-26':
        return 'Jan 8-26'
    elif timeline == 'I am available the first two weeks from Jan 8-19':
        return 'Jan 8-19'
    elif timeline == 'I am available the last two weeks from Jan 15-26':
        return 'Jan 15-26'
    else:
        return timeline

class Level(Enum):
    INTRO = 1
    INTERMEDIATE = 2
    ADVANCED = 3

def get_student_level(student):
    if not student['cs']:
        return Level.INTRO
    elif student['class'] != 'Freshman' and student['major'] == 'Computer Science':
        return Level.ADVANCED
    else:
        return Level.INTERMEDIATE

def get_student_profile(student):
    profile = {}
    interests = get_interests(student)

    profile['email'] = student['Email']
    profile['gender'] = student['Gender']
    profile['interests'] = interests
    profile['size'] = student['Size']
    profile['computer'] = yesno_to_tf(student, 'Computer')
    profile['Macaulay'] = yesno_to_tf(student, 'Macaulay')
    profile['Guild'] = yesno_to_tf(student,'Guild')
    profile['Legal'] = yesno_to_tf(student, 'Legal')
    profile['cuny'] = student['CUNY']
    profile['travel'] = yesno_to_tf(student, 'Travel')
    profile['class'] = student['Class']
    profile['major'] = student['Major']
    profile['graduation'] = get_grad_year(student)
    profile['timeline'] = get_student_timeline(student)
    profile['commitment'] = student['Commitment']
    profile['cs'] = yesno_to_tf(student, 'CS Class')

    # short answers
    passionate = student['Passionate']
    goals = student['Goals']
    learn = student['Hope to learn']
    career = student['Interest in a tech career']
    team = student['Team experiences']
    whyme = student['Why you']
    list_interests = student['Interests']

    profile['short_answers'] = [passionate, goals, learn, career, team, whyme, list_interests]

    return profile


def interests_match(student_interests, company_interests):
    total = 0
    for interest in company_interests:
        if interest in student_interests:
            total += 1
    return total

def student_company_match(student_p, company_p):
    location_match = student_p['travel'] or (company_p['location'] == 'NYC')
    schedule_match = True
    # schedule_match = (student_p['timeline'] == company_p['timeline'])
    size_match = (student_p['size'].lower() == company_p['size'].lower())
    if location_match and schedule_match:
        student_commitment = student_p['commitment'] == 'Very Committed'
        return interests_match(student_p['interests'], company_p['interests']) + size_match + student_commitment
    else:
        return -1

def short_answers_ok(answers):
    for ans in answers:
        if len(ans) < 10:
            return False
    return True

def student_commitment(level):
    return level == 'Committed' or \
        level == 'Very Committed'

def student_ok(student_profile):
    return student_profile['Legal'] and \
        short_answers_ok(student_profile['short_answers']) and \
        student_profile['gender'] != 'Male' and \
        student_commitment(student_profile['commitment'])

# TODO: add a reason to bad students...
def separate_bad_students(student_profiles):
    good, bad = [], []
    for student_profile in student_profiles:
        if student_ok(student_profile):
            good.append(student_profile)
        else:
            bad.append(student_profile)
    return good, bad

def get_score(results):
    total = 0
    for k in results.keys():
        total += (k * results[k])
    return total


def get_number_of_compatible_students(results):
    total = 0
    for k in results.keys():
        if k != -1:
            total += results[k]
    return total

def assess_results(students, company_profiles):
    score = {}
    for company in company_profiles:
        results = {}
        for student in students:
            match = student[company]
            if match in results:
                results[match] += 1
            else:
                results[match] = 0
        score[company] = get_score(results)
        # score[company] = get_number_of_compatible_students(results)
    return score

def get_requirements():
    requirements = {}
    requirements['sophomore'] = lambda s: (s['class'] != 'Freshman')
    requirements['advanced'] = lambda s: (s['CS Level'] == 'ADVANCED')
    requirements['intermed'] = lambda s: (s['CS Level'] == 'INTERMEDIATE')
    # this is probably a bad idea bc it eats some students
    requirements['2nd intermed'] = lambda s: (s['CS Level'] == 'INTERMEDIATE')
    requirements['sg'] = lambda s: (s['Guild'])
    requirements['honors'] = lambda s: (s['Macaulay'])
    requirements['different school'] = lambda s: (s['cuny'] != 'Baruch College' and s['cuny'] != 'Hunter College')
    requirements['non-CS freshman'] = lambda s: (s['class'] == 'Freshman' and \
                                                s['major'] != 'Computer Science' and \
                                                s['major'] != 'CS')
    return requirements

def build_teams(requirements, companies_ordered_by_matches, students):
    matched_students = {}
    all_matches = []
    for company in companies_ordered_by_matches:
        remaining_reqs = list(requirements)
        # sort list of students by company column, from highest score to lowest
        list.sort(students, key=(lambda s: s[company]), reverse=True)
        matches = []
        for student in students:
            # once we're into students who don't match on location, there won't be any more good matches
            if student[company] == -1:
                break
            
            # or we might have reached the max team size
            if len(matches) == 5:
                break

            for req in remaining_reqs:
                if(requirements[req](student)):
                    # if this is the first requirement they matched on:
                    if student not in matches:

                        # change their match score
                        student[company] = 'M' + str(student[company])

                        # remove them from the blank students list
                        students.remove(student)

                         # add them to the company list
                        matches.append(student)
                        all_matches.append(student)

                        # change their status for all other companies...
                        for c2 in companies_ordered_by_matches:
                            if c2 != company:
                                student[c2] = 'A' + str(student[c2])


                    # print(student['email'], 'matches', company, 'on', req, 'with score of', student[company])
                    remaining_reqs.remove(req)
        matched_students[company] = matches

    # do a second pass to fill in the gaps
    reordered_companies = order_companies_by_student_scores(students, companies_ordered_by_matches)

    for company in reordered_companies:
        matches = matched_students[company]
        list.sort(students, key=(lambda s: s[company]), reverse=True)
        while len(matches) < 5:
            student = students.pop(0)
            # you can't assign an unacceptable match
            if student[company] == -1:
                break

            student[company] = 'M' + str(student[company])
            matches.append(student)
            all_matches.append(student)

            for c2 in companies_ordered_by_matches:
                if c2 != company:
                    student[c2] = 'B' + str(student[c2])

    print("students who didn't match:", len(students))
    for company in matched_students:
        if len(matched_students[company]) < 5:
            print(company, 'has only', len(matched_students[company]), 'students matched')
    return all_matches + students

# def write_out_students(student_profiles, headers):

def order_companies_by_student_scores(students, companies):
    scores = assess_results(students, companies)
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))
    companies_ordered_by_matches = [x for (x,y) in sorted_scores]
    return companies_ordered_by_matches

if __name__ == '__main__':
    students = read_file('students.csv')
    companies = read_file('companies.csv')

    s_data = {student['Email']: student for student in students}

    student_profiles = [get_student_profile(student) for student in students]
    good_students, bad_students = separate_bad_students(student_profiles)
    company_profiles = [get_company_profile(company) for company in companies]

    print (len(student_profiles))
    print(len(good_students))
    print(len(bad_students))
    print (len(company_profiles))

    # create baseline list of headers
    h0 = list(students[0].keys()) + ['CS Level']
    extra_keys = ['Phone', 'Legal', 'When', 'Travel', 'Computer', 'How did you hear']
    for key in extra_keys:
        h0.remove(key)

    for student_profile in good_students:
        email = student_profile['email']
        student_profile['CS Level'] = get_student_level(student_profile).name
        for company_profile in company_profiles:
            match = student_company_match(student_profile, company_profile)
            student_profile[company_profile['name']] = match
        

    companies_ordered_by_matches = order_companies_by_student_scores(good_students, [c['name'] for c in company_profiles])

    requirements = get_requirements()
    students_final = build_teams(requirements, companies_ordered_by_matches, good_students)

    for student_profile in students_final:
        email = student_profile['email']
        s_dict = s_data[email]
        s_dict['CS Level'] = student_profile['CS Level']

        # remove some stuff that you don't need
        for key in extra_keys:
            del s_dict[key]
        
        # update the company scores
        for company_profile in company_profiles:
            company = company_profile['name']
            s_dict[company] = student_profile[company]

    headers = h0 + companies_ordered_by_matches
    with open('matches.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()
        for student in students_final:
            email = student['email']
            writer.writerow(s_data[email])