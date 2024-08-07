import requests
import json

with open('moe.json') as f:
    data = json.load(f)

schools_json = data['response']['docs']

schools_data = {}

# iterate through the schools_json and extract the data we are interested in
for school in schools_json:
    school_name = school['school_name_s']
    schools_data[school_name] = {
        'address': school['address_s'],
        'postal_code': school['postal_code_s'],
        'town': school['school_area_t']
    }

assert len(schools_data) == 182, "There should be 182 schools in the list"

# call the onemap api on each school and add the latitude and longitude to the school data
for key in schools_data:
    school = schools_data[key]
    search_postal = school['postal_code']
    response = requests.get('https://www.onemap.gov.sg/api/common/elastic/search?searchVal='+search_postal+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    results = eval(response.text)
    try:
        school['latitude'] = results['results'][0]['LATITUDE']
        school['longitude'] = results['results'][0]['LONGITUDE']
    except:
        print('Error: ', school['name'], school['postal_code'])
        school['latitude'] = None
        school['longitude'] = None

# print(schools_data)

# write the schools_data to a csv file
with open('schools.csv', 'w') as f:
    f.write('school_name,address,postal_code,town,latitude,longitude\n')
    for key in schools_data:
        school = schools_data[key]
        f.write(key + ',' + school['address'] + ',' + school['postal_code'] + ',' + school['town'] + ',' + school['latitude'] + ',' + school['longitude'] + '\n')



'''
MOE JSON DATA WAS TAKEN FROM:
	https://search.moe.gov.sg/solr/moe_school_index/select?q=*&fq=school_journey_ss:"Primary school"&fq=active_b:true&sort=slug_s asc&rows=200&start=0&json.facet={school_area:{type:terms,field:school_area_s,limit:-1,sort:index,domain:{excludeTags:"area"}},co_cirricular_activities_full_path:{type:terms,field:co_cirricular_activities_full_path,limit:-1,sort:index},subjects_offered_trimmed:{type:terms,field:subjects_offered_trimmed_ss,limit:-1,sort:index},electives_full_path:{type:terms,field:electives_full_path,limit:-1,sort:index},special_needs:{type:terms,field:special_needs_ss,limit:-1,sort:index,domain:{excludeTags:"specialNeeds"}},school_type:{type:terms,field:school_type_ss,limit:-1,sort:index,domain:{excludeTags:"type"}},school_other_programme:{type:terms,field:school_other_programme_ss,limit:-1,sort:index,domain:{excludeTags:"otherProgramme"}},school_status_type:{type:terms,field:school_status_type_ss,limit:-1,sort:index},school_affiliated_b:{type:terms,field:school_affiliated_b_ss,limit:-1,sort:index},school_nature:{type:terms,field:school_nature_s,limit:-1,sort:index,domain:{excludeTags:"nature"}}}
'''
