import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_trucks_data():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('reefer.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Warehousing Sheet Data Feed')
    data = sheet.worksheet('EXPORT')
    trucks = data.get_all_values()
    return trucks

def create_truck(truck_list):
    truck_dict = {}
    truck_dict['load_no'] = truck_list[0]
    truck_dict['married_load'] = truck_list[1]
    truck_dict['truck_no'] = truck_list[2]
    truck_dict['carrier_name'] = truck_list[3]
    truck_dict['dispatched'] = truck_list[4]
    return truck_dict