from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import zoneinfo
from functools import lru_cache

browser = webdriver.Chrome()
plan_a = [
    "33722d9f-8222-46c6-a50c-d2efdb7138b2",  # Helmet falls
    "cee0ea4b-7042-4723-ad2f-a2bba86bc177",  # Tumbling creek
    "0787d348-df8b-475e-a59c-150088d91409",  # Numa creek
    "b8af6f3c-60f5-4719-9326-2f2bf5d0e89c",  # Floe lake
]
plan_b = [
    "33722d9f-8222-46c6-a50c-d2efdb7138b2",  # Helmet falls
    "cee0ea4b-7042-4723-ad2f-a2bba86bc177",  # Tumbling creek
    "b8af6f3c-60f5-4719-9326-2f2bf5d0e89c",  # Floe lake
]
paint_pots_trailhead = "6bd4c856-aabc-4f96-b5ce-9aa370721949"
floe_lake_trailhead = "1b8bafc3-e472-42be-a656-a355d2a8299a"


@lru_cache(maxsize=None)
def get_timezones():
    return zoneinfo.available_timezones()


def close_popup(btn_xpath):
    attempts = 0
    while attempts < 5:
        try:
            browser.find_element(By.XPATH, btn_xpath).click()
            return
        except StaleElementReferenceException:
            time.sleep(0.5)
            print("Failed again")
        attempts += 1


def find_and_select(elem_type, element, value, sleep_interval=0.0):
    elem = Select(browser.find_element(elem_type, element))
    elem.select_by_value(value)
    if sleep_interval > 0:
        time.sleep(sleep_interval)


def find_tent_sites():
    row_id = 0
    for site_val in plan:
        # Select s
        find_and_select(By.ID, 'selItineraryResource', site_val, 1.0)
        # Check for errors encountered for this site selection
        err = list(browser.find_elements(By.ID, 'itineraryErrorRow' + str(row_id)))
        if len(err) > 0:
            print('RESERVATION FAILED FOR THESE DATES!')
            # return False
        row_id += 1
    return True


def get_first_day_of_month(dte):
    return dte.replace(day=1)


def format_date_to_str(dte):
    return dte.strftime('%a %b %d %Y %H:%M:%S') + " GMT-0700 (Pacific Daylight Time)"


def book_it(start_date, trailhead):
    browser.get('https://reservation.pc.gc.ca/Banff,KootenayandYohoBackcountry?List')

    # Select 'Backcountry' camping from reservation dropdown menu
    find_and_select(By.NAME, 'selResType', 'Backcountry', 4)
    # Close popup windows
    tmp = list(browser.find_elements(By.ID, 'popupMessagePanel'))
    if len(tmp) > 0:
        close_popup("//*[@id='pageBody']/div[3]/div[1]/button/span[1]")
    # Select arrival date from dropdown menus
    find_and_select(By.ID, 'selArrMth', format_date_to_str(get_first_day_of_month(start_date)), 1.5)
    find_and_select(By.ID, 'selArrDay', format_date_to_str(start_date), 1.5)
    # Select Party size
    find_and_select(By.ID, 'selPartySize', '4', 1.5)
    # Select Number of Tent pads
    find_and_select(By.ID, 'selTentPads', '2', 1.5)
    # Select Access Point
    find_and_select(By.ID, 'MainContentPlaceHolder_AccessPointList', trailhead, 2)

    # Select Tent Sites
    success = find_tent_sites()
    return success


if __name__ == '__main__':
    start_dates = [
        datetime(2023, 8, 31, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("America/Vancouver")),
        datetime(2023, 9, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("America/Vancouver"))
    ]
    counter = 0
    for plan in [plan_a, plan_b]:
        counter += 1
        for start in start_dates:
            if book_it(start, paint_pots_trailhead):
                plan_type = "Plan A: 4 nights/5 days" if counter == 1 else "Plan B: 3 nights/4 days"
                print(f"{plan_type} - Starting on:{start}")
                break
