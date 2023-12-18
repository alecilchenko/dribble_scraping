from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    ElementClickInterceptedException
)
import time
import random
import json


def get_delay():
    return random.uniform(20, 40)


def sign_form(driver, name, password):
    url = 'https://dribbble.com/session/new'
    driver.get(url)
    driver.find_element(By.ID, 'login').send_keys(name)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(
        By.XPATH,
        '/html/body/div/section[2]/main/div/div[2]/form/input[3]'
    ).click()
    return driver


def like_value(screenshot):
    selector = 'div.shot-details-container.js-shot-details-container > ' \
               'div.shot-statistics-container.js-shot-statistics > ' \
               'div.shot-statistic.js-shot-likes-container > span'
    detail_cont = screenshot.find_element(By.CSS_SELECTOR, selector)
    return detail_cont.text


def analyse_shots(shots):
    shots_dict = {}
    for shot in shots:
        if shot not in shots_dict:
            try:
                value = int(like_value(shot))
                shots_dict[shot] = value
            except ValueError:
                value = like_value(shot)
                if '.' in value:
                    value.replace('.', '').replace('k', '00')
                else:
                    value.replace('k', '000')
                value = int(value)
                shots_dict[shot] = value
    return shots_dict


def get_like(shots_dict, max_shot_likes):
    count = 1
    for shot, likes in shots_dict.items():
        if int(likes) < max_shot_likes:
            try:
                shot.find_element(By.ID, 'shots-like-button').click()
                print(count)
                count += 1
                time.sleep(get_delay())
            except NoSuchElementException:
                continue
            except ElementClickInterceptedException:
                continue


def get_comment(driver, shot, comment, used_shots_list):
    shot.click()
    time.sleep(get_delay())
    if driver.current_url not in used_shots_list:
        comment_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button.btn2:nth-child(1) > svg:nth-child(1)"
        )
        comment_btn.click()
        time.sleep(get_delay())

        form_1 = driver.find_element(By.ID, 'shot-sidebar-app')
        form_2 = form_1.find_element(By.CLASS_NAME, 'shot-sidebar-content')
        form_3 = form_2.find_element(By.CLASS_NAME, 'shot-comments-post')
        fill_4 = form_3.find_element(By.CLASS_NAME, 'textarea-form')
        fill_form_text = fill_4.find_element(By.CLASS_NAME, 'textarea-field')
        fill_form_text.send_keys(comment)
        time.sleep(get_delay())
        post_btn = driver.find_element(
            By.XPATH,
            '//*[@id="shot-sidebar-app"]'
            '/div/div/div/div/div[2]/form/div/button'
        )
        used_shots_list.append(driver.current_url)
        time.sleep(get_delay())
        post_btn.click()
        time.sleep(get_delay())

    close_1 = driver.find_element(By.CLASS_NAME, "shot-overlay")
    close_btn = close_1.find_element(By.CLASS_NAME, 'js-close-overlay')
    close_btn.click()
    time.sleep(get_delay())
    return used_shots_list


def distribute_comments(driver, shots_dict):
    count = 1
    with open("comments.json", "r") as json_file:
        comments_list = json.load(json_file)
    with open("used_shots.json", 'r') as json_file:
        used_shots_list = json.load(json_file)

    for shot, likes in shots_dict.items():
        if int(likes) > 120:
            try:
                shot.find_element(By.ID, 'shots-like-button').click()
                time.sleep(get_delay())
                comment = random.choice(comments_list)
                used_shots_list = get_comment(
                    driver, shot,
                    comment, used_shots_list
                )
                count += 1
            except NoSuchElementException:
                continue
            except ElementClickInterceptedException:
                continue

    with open("used_shots.json", "w") as json_file:
        json.dump(used_shots_list, json_file)


def scroll_down(driver, amount):
    max_web_iteration = 0
    content = driver.find_element(By.ID, 'wrap')
    last_height = content.size['height']
    shots = driver.find_elements(By.XPATH, "//*[contains(@id, 'screenshot')]")
    while True:
        driver.execute_script(f"window.scrollTo(0, {last_height});")
        time.sleep(get_delay())
        new_height = content.size['height']
        if new_height == last_height:
            try:
                btn_1 = driver.find_element(By.ID, 'wrap')
                btn_2 = btn_1.find_element(By.ID, 'content')
                btn_3 = btn_2.find_element(By.ID, 'main')
                btn_4 = btn_3.find_element(By.CLASS_NAME, 'infinite')
                button = btn_4.find_element(By.CLASS_NAME, 'form-btn')
                button.click()
                time.sleep(get_delay())
                shots = driver.find_elements(
                    By.XPATH,
                    "//*[contains(@id, 'screenshot')]"
                )
                if len(shots) > amount:
                    break
            except NoSuchElementException:
                continue
            except WebDriverException:
                max_web_iteration += 1
                if max_web_iteration >= 10:
                    return shots, driver
                continue
        last_height = new_height
        time.sleep(get_delay())
    return shots, driver


def driver_set_up():
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install())
    )
    driver.maximize_window()
    with open("credentials.txt", "r") as file:
        data = file.read()
    name, password = data.split()
    while True:
        try:
            driver = sign_form(
                driver,
                name=name,
                password=password
            )
            driver.get('https://dribbble.com/shots/recent')
            break
        except WebDriverException:
            time.sleep(get_delay())
    return driver


def like_case(max_shot_likes, max_shots_scroll):
    driver = driver_set_up()
    shots_list, driver = scroll_down(driver, max_shots_scroll)
    shots_dict = analyse_shots(shots_list)
    get_like(shots_dict, max_shot_likes)


def comment_case(max_shots_scroll):
    driver = driver_set_up()
    shots_list, driver = scroll_down(driver, amount=max_shots_scroll)
    shots_dict = analyse_shots(shots_list)
    distribute_comments(driver, shots_dict)


if __name__ == '__main__':
    like_case(20, 500)
    comment_case(500)
