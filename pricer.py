# TODO module and variable naming; how to structure 'selling_price' variable

import getpass
import logging
import logging.config
import os
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
import tms_login as tms
import discount
# import discount_sept as discount
import passport
import wildbrine
# import pocino
import papacantella


def enter_billing(load, price, discount_amt=0):
    # url = 'http://boa.3plsystemscloud.com/'
    try:
        edit_pricing = (
            f'{url}App_BW/staff/shipment/shipmentCostPop.aspx?loadid={load}'
            )
        browser.get(edit_pricing)

        td_list = browser.find_elements_by_tag_name('td')
        ship_cost_pos = [td.text for td in td_list].index('Shipping Costs:')
        # input box in next TD cell after Shipping Cost label
        ship_cost_cell = td_list[ship_cost_pos + 1]
        ship_cost_input = ship_cost_cell.find_element_by_tag_name('input')
        if ship_cost_input.get_attribute('value'):
            ship_cost_input.send_keys(Keys.CONTROL + 'a')
            ship_cost_input.send_keys(Keys.DELETE)
            ship_cost_input.send_keys(str(price))
            logging.info(f'{load} Base retail: {price}')
        else:
            logging(f'{load} already has existing pricing.')

        if discount_amt:
            discount.apply_discount(load, discount_amt, browser)
            logging.info(f'{load} discounted {discount_amt} ({float(discount_amt) / price})')


        save_price_btn = browser.find_element_by_id('btnUpdateCosts')
        save_price_btn.click()
    except Exception as e:
        logging.info(f'{load} threw {repr(e)}')


# initialize logger
logging.config.fileConfig(fname='logs/cfg/price.conf')
logger = logging.getLogger('')

# # set to Chrome default download folder - BOA CITRIX DESKTOP DEFAULT SETTINGS
DOWNLOAD_FOLDER = f"C:\\Users\\{getpass.getuser().title()}\\Downloads"

# list of files before downloading
before = os.listdir(DOWNLOAD_FOLDER)

url = 'https://boa.3plsystemscloud.com/'
browser = tms.login(url, False)

# enter report code into REPORT_CODE constant
# "Pricer / Discounter" report
REPORT_CODE = '23725A2291F1'
report_url = f'{url}App_BW/staff/Reports/ReportViewer.aspx?code={REPORT_CODE}'
browser.get(report_url)

loadlist = ['142037', '143263', '143264', '143466', '143613', '143780', '143896', '143897', '143898', '143899', '143900', '143901', '144003', '144004', '144159', '144160', '144161', '144306', '144352', '144540', '144541', '145113', '145114', '145115', '145116', '145117', '145135', '145136', '145611', '145612', '145623', '145774', '145775', '145776', '145792', '145793', '146313', '146499', '146596', '146636', '146944', '147142', '147143', '147239', '147412', '147647', '147648', '147649', '147650', '147651', '147652', '147653', '147654', '147655', '147673', '147781', '147783', '148075', '148344', '148345', '148346', '148662', '148953', '148974', '148975', '149104', '149138', '149267', '149339', '149632', '149633', '149634', '149635', '149763', '149764', '149884', '149885', '149886', '149887', '150144', '150145', '150274', '150371', '150386', '150426', '150467', '150468', '150477', '150611', '150612', '150968', '150994', '151030', '151031', '151033', '151034', '151035', '151237', '151301', '151305', '151306', '151307', '151439', '151495', '151496', '151537', '151539', '151541', '151542', '151548', '151549', '151597', '151605', '152363', '152364', '154491', '154492', '154493', '154494', '154495', '154496', '154497', '154498', '154499', '154500', '154743', '154744', '154949', '154950', '154951', '154952', '154953', '154954', '154955', '154956', '155074', '155075', '155077', '155078', '155162', '155720', '155820', '155821', '155827', '155828', '155876', '155877', '155878', '155879', '155920', '155955', '155956', '155958', '155959', '156188', '156353', '156354', '156355', '156356', '156357', '156358', '156362', '156363', '156364', '156365', '156368', '156435', '156436', '156599', '156600', '157828', '157829', '157830', '157831', '157832', '157833', '157858', '157859', '157875', '157892', '157893', '157894', '157920', '157922', '157924', '157926', '157927', '158045', '158046', '159154', '159208', '159209', '159210', '159217', '159225', '159226', '159229', '159230', '159231', '159232', '159286', '159287', '159532', '159639', '159640', '159644', '159645', '159739', '159740', '159742', '159743', '159744', '159745', '159746', '159747', '159748', '159941', '159942', '160065', '160299', '160300', '160301', '160302', '160303', '160304', '160311', '160312', '160313', '160366', '160367', '160825', '160826', '160827', '160828', '160830', '160832', '160833', '160834', '160860', '160890', '160891', '161007', '161008', '161429', '161430', '161431', '161432', '161433', '161456', '161457', '161458', '161459', '161462', '161545', '161546', '161570', '161571', '161918', '161919', '161920', '161921', '161922', '161923', '161926', '161927', '161987', '162115', '162116', '162459', '162460', '162461', '162462', '162463', '162464', '162465', '162466', '162517', '162540', '162671', '162672', '162697', '162698', '162769', '162770', '162771', '162772', '162773', '162774', '162975', '163086', '163087', '163088', '163089', '163093', '163094', '163095', '163096', '163194', '163273', '163274', '163619', '163620', '163622', '163623', '163650', '163651', '163652', '163653', '163654', '163875', '163876', '163886', '163887', '164131', '164132', '164133', '164134', '164135', '164136', '164175', '164176', '164327', '164328', '164362', '164363', '164364', '164367', '164369', '164370', '164371', '164478', '164479', '164501', '164809', '164810', '164841', '164842', '164843', '164844', '164845', '164846', '164875', '165010', '165011', '165012', '165084', '165085', '165086', '165087', '165444', '166144', '166145', '166146', '166147', '166148', '166149', '166150', '166151', '166315', '166316', '166403', '166404', '166406', '166407', '166408', '166409', '166410', '166411', '166431', '166432', '166808', '166810', '166811', '166812', '166813', '166814', '166815', '166816', '166921', '167011', '167012', '167136', '167137', '167431', '167432', '167433', '167434', '167436', '167437', '167438', '167456', '167540', '167584', '167590', '167595', '167663', '167664', '167854', '167855', '167856', '168126', '168134', '168135', '168199', '168200', '168201', '168202', '168203', '168211', '168266', '168267', '168268', '168336', '168337', '168341', '168342', '168479', '168482', '168505', '168724', '168751', '168768', '168769', '168770', '168771', '168782', '168783', '168784', '168785', '168950', '168951', '168952', '168953', '169154', '169155', '169330', '169395', '169448', '169451', '169452', '169470', '169471', '169472', '169473', '169474', '169963', '169972', '169973', '169974', '169977', '169990', '169991', '170020', '170021', '170038', '170052', '170053', '170054', '170060', '170061', '170166', '170170', '170175', '170176', '170177', '170473', '170474', '170491', '170492', '170495', '170525', '170607', '170608', '170632', '170633', '170634', '170635', '170636', '170637', '170638', '170639', '170726', '170761', '170976', '170990', '170991', '171034', '171072', '171136', '171178', '171179', '171180', '171181', '171187', '171188', '171189', '171190', '171191', '171192', '171193', '171194', '171254', '171412', '171528', '171529', '171530', '171531', '171683', '171684', '171685', '171723', '171797', '171798', '171799', '171800', '171801', '171802', '171803', '171804', '171918', '171919', '171922', '171923', '171924', '171925', '171926', '171927', '171929', '172071', '172208', '172209', '172210', '172216', '172218', '172219', '172223', '172224', '172380', '172430', '172431', '172457', '172458', '172459', '172460', '172461', '172462', '172463', '172464', '172696', '172878', '172933', '173031', '173032', '173054', '173055', '173065', '173066', '173067', '173068', '173069', '173070', '173260', '173307', '173595', '173655', '173656', '173690', '173691', '173692', '173693', '173719', '173720', '173721', '173722', '174206', '174207', '174300', '174301', '174334', '174335', '174410', '174473', '174511', '174529', '174678', '174704', '174822', '174911', '174914', '174917', '174919', '174921', '174922', '174923', '175181']

loadno = browser.find_element_by_xpath("//td[1]/input[@class='filter']")
loadno.clear()
for x in loadlist[:-1]:
    loadno.send_keys(f'\'{x}\',')
loadno.send_keys(f'\'{loadlist[-1]}\'')

# save & view report, then download
save_report_btn = browser.find_element_by_id('ctl00_ContentBody_butSaveView')
save_report_btn.click()
browser.implicitly_wait(3)
download = browser.find_element_by_id('ctl00_ContentBody_butExportToExcel')
download.click()
time.sleep(1)

# list of files in Downloads folder after downloading to extract filename
after = os.listdir(DOWNLOAD_FOLDER)
change = set(after) - set(before)

if len(change) == 1:
    file_name = change.pop()
    logging.info(f'{file_name} downloaded.')
elif len(change) == 0:
    logging.info('No file downloaded.')
else:
    logging.info('More than one file downloaded.')

# output file extension is .xls but is actually.html format
filepath = f'{DOWNLOAD_FOLDER}\\{file_name}'
# filepath = 'Pricer_Discounter20201106.xls'
data = pd.read_html(filepath)
df = data[0]
load_table = df[[
    'Load #', 'Consignee', 'S/ City', 'S/ State', 'C/ City',
    'C/ State', 'C/ Zip', 'Equipment', 'Pallets', 'Weight', 'Base Retail', 'Cost', 'Billed', 'Customer #'
    ]].drop(len(df.index)-1)

# TODO store client name + id in json
passport_df = load_table[load_table['Customer #'] == 1495]
stir_df = load_table[load_table['Customer #'] == 1374]
wildbrine_df = load_table[load_table['Customer #'] == 890]
papacantella_df = load_table[load_table['Customer #'] == 1232]
pocino_df = load_table[load_table['Customer #'] == 933]

export_df = pd.DataFrame([['Load', 'City-State', 'Pallets', 'Base Retail', 'Margin']])

if len(passport_df.index) > 0:
    passport_df.reset_index(drop=True, inplace=True)
    for row in passport_df.index:
        current_row = passport_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 21 or current_row['C/ City'] == 'Mira Loma' or current_row['C/ City'] == 'Tracy':
                selling_price = passport.get_price(current_row)
                enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 20 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_load, current_cs, current_plts, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)
        
if len(stir_df.index) > 0:
    stir_df.reset_index(drop=True, inplace=True)
    for row in stir_df.index:
        current_row = stir_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        margin = '-'

        try:
            current_row = stir_df.iloc[row]
            # TODO how to account for rates not on table? and manually entered existing?
            # check if Base Retail == 0
            selling_price = discount.get_price(current_row)
            discount_amt = discount.get_discount(current_row, selling_price[1])
            enter_billing(*selling_price, discount_amt)
            margin = (current_row['Billed'] + selling_price[1] - current_row['Cost'] + discount_amt) / (current_row['Billed'] + selling_price[1])
            logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            # print(*selling_price, discount_amt)
        except Exception as e:
            logging.info(str(current_row['Load #']) +  ' errored. No rate found for ' + repr(e))

        export_row = pd.DataFrame([[current_load, current_cs, current_plts, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(wildbrine_df.index) > 0:
    # wildbrine_df.reset_index(drop=True, inplace=True)
    for row in wildbrine_df.index:
        current_row = wildbrine_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 10:
                selling_price = wildbrine.get_price(current_row)
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 9 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_load, current_cs, current_plts, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

if len(papacantella_df.index) > 0:
    # papacantella_df.reset_index(drop=True, inplace=True)
    for row in papacantella_df.index:
        current_row = papacantella_df.iloc[row]
        current_load = current_row['Load #']
        current_plts = current_row['Pallets']
        # current_retail = current_row['Base Retail']
        current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
        margin = '-'

        # if current_retail != 0.0:    
        try:
            if current_plts < 15:
                selling_price = papacantella.get_price(current_row)
                # enter_billing(*selling_price)
                margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
                logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
            else:
                logging.info(str(current_load) + ' exceeds 14 pallets: ' + str(current_plts))
        except Exception as e:
            logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
        # else:
        #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
        export_row = pd.DataFrame([[current_load, current_cs, current_plts, margin]])
        export_df = pd.concat([export_df, export_row], ignore_index=False)

# if len(pocino_df.index) > 0:
#     # pocino_df.reset_index(drop=True, inplace=True)
#     for row in pocino_df.index:
#         current_row = pocino_df.iloc[row]
#         current_load = current_row['Load #']
#         current_plts = current_row['Pallets']
#         # current_retail = current_row['Base Retail']
#         current_cs = current_row['C/ City'] + ', ' + current_row['C/ State']
#         selling_price =['-', '-']
#         margin = '-'

#         # if current_retail != 0.0:    
#         try:
#             if current_plts < 16:
#                 selling_price = pocino.get_price(current_row)
#                 # enter_billing(*selling_price)
#                 margin = (current_row['Billed'] + selling_price[1] - current_row['Cost']) / (current_row['Billed'] + selling_price[1])
#                 logging.info(str(current_load) + ' ' + current_cs + ' margin: ' + str(margin) + ', pallets: ' + str(current_plts))
#             else:
#                 logging.info(str(current_load) + ' exceeds 15 pallets: ' + str(current_plts))
#         except Exception as e:
#             logging.info(str(current_load) +  ' errored. No rate found for ' + repr(e))
#         # else:
#         #     logging.info(str(current_load) + ' already has base retail entered: ' + str(current_retail))
        
#         export_row = pd.DataFrame([[current_load, current_cs, current_plts, selling_price[1], margin]])
#         export_df = pd.concat([export_df, export_row], ignore_index=False)

# browser.quit()
# print('Browser closed.')

print('Opening log file...')
os.startfile('logs\\pricer.log')

print('Exporting summary to Excel...')
writer = pd.ExcelWriter('logs\\pricer.xlsx', engine="xlsxwriter")
export_df.to_excel(writer, sheet_name='pricer')
writer.save()
os.startfile('logs\\pricer.xlsx')

print('Done!')