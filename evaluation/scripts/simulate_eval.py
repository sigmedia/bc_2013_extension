#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR

    Sébastien Le Maguer <lemagues@surface>

DESCRIPTION

LICENSE
    This script is in the public domain, free from copyrights or restrictions.
    Created: 10 January 2022
"""

# Arguments
import argparse

# Messaging/logging
import logging
from logging.config import dictConfig

# Helpers
import math
import random
import time

# Processes/System
from multiprocessing import Pool
import sys

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

###############################################################################
# global constants
###############################################################################
LEVEL = [logging.WARNING, logging.INFO, logging.DEBUG]

###############################################################################
# Functions
###############################################################################
def configure_logger(args) -> logging.Logger:
    """Setup the global logging configurations and instanciate a specific logger for the current script

    Parameters
    ----------
    args : dict
        The arguments given to the script

    Returns
    --------
    the logger: logger.Logger
    """
    # Verbose level => logging level
    log_level = args.verbosity
    if args.verbosity >= len(LEVEL):
        log_level = len(LEVEL) - 1
        # logging.warning("verbosity level is too high, I'm gonna assume you're taking the highest (%d)" % log_level)

    # Define the default logger configuration
    logging_config = dict(
        version=1,
        disable_existing_logger=True,
        formatters={
            "f": {
                "format": "[%(asctime)s] [%(levelname)s] — [%(name)s — %(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%d/%b/%Y: %H:%M:%S ",
            }
        },
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": LEVEL[log_level],
            }
        },
        root={"handlers": ["h"], "level": LEVEL[log_level]},
    )

    # Add file handler if file logging required
    if args.log_file is not None:
        logging_config["handlers"]["f"] = {
            "class": "logging.FileHandler",
            "formatter": "f",
            "level": LEVEL[log_level],
            "filename": args.log_file,
        }
        logging_config["root"]["handlers"] = ["h", "f"]

    # Setup logging configuration
    dictConfig(logging_config)

    # Retrieve and return the logger dedicated to the script
    logger = logging.getLogger(__name__)
    return logger


def define_argument_parser() -> argparse.ArgumentParser:
    """Defines the argument parser

    Returns
    --------
    The argument parser: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="")

    # Add options
    parser.add_argument(
        "-b",
        "--browser",
        default="chromium",
        type=str,
        help="The browser used by selenium",
    )
    parser.add_argument(
        "-n", "--nb_procs", default=1, type=int, help="The number of parallel processes"
    )
    parser.add_argument(
        "-u",
        "--url",
        default="http://localhost:8080/",
        type=str,
        help="The FlexEval instance URL",
    )

    # Logging options
    parser.add_argument("-l", "--log_file", default=None, help="Logger file")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )

    # Return parser
    return parser


###############################################################################
#  Selenium helpers
###############################################################################
def safe_send_keys(
    driver, input_selector: str, input_text: str, selector_type=By.CSS_SELECTOR
):
    driver.find_element(selector_type, input_selector).click()
    action = ActionChains(driver)
    action.send_keys(input_text)
    action.perform()


def sleep_wrapper(sleep_duration):
    global logger
    logger.debug(f"I have been asked to sleep for {sleep_duration:.03f}s")
    # time.sleep(sleep_duration)
    # time.sleep(1)


def play_sample(driver):
    if isinstance(driver, webdriver.firefox.webdriver.WebDriver):
        # driver.find_element(By.ID, "sample").click();
        driver.execute_script("document.getElementById('sample').play();")
    else:
        driver.execute_script("document.getElementById('sample').play();")


def click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def test_similarity_step(driver, sleep_duration):
    global logger
    # Get Duration
    audio = driver.find_element(By.ID, "sample")
    str_audio = audio.get_attribute("duration")
    duration = float(audio.get_attribute("duration"))

    # Play
    time.sleep(1)
    if math.isnan(duration):
        print(str_audio)
        time.sleep(30)
    logger.debug(
        f"Play sample and wait {math.ceil(duration) + 1}s for the activation of the submission button"
    )
    play_sample(driver)
    ui.WebDriverWait(driver, math.ceil(duration) + 1).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )

    # Grade
    select = ui.Select(driver.find_element(By.TAG_NAME, "select"))
    select.select_by_value(f"{random.randint(1, 5)}")

    # Validate
    logger.debug("Validate")
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(sleep_duration)
    click(driver, submit)


def test_mos_step(driver, sleep_duration):

    # Get Duration
    audio = driver.find_element(By.ID, "sample")
    duration = float(audio.get_attribute("duration"))

    # Play
    logger.debug(
        f"Play sample and wait {math.ceil(duration) + 1}s for the activation of the submission button"
    )
    play_sample(driver)
    ui.WebDriverWait(driver, math.ceil(duration) + 1).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )

    # Grade
    select = ui.Select(driver.find_element(By.TAG_NAME, "select"))
    select.select_by_value(f"{random.randint(1, 5)}")

    # Validate
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(sleep_duration)
    click(driver, submit)


def test_intel_step(driver, sleep_duration):

    # Get Duration
    audio = driver.find_element(By.ID, "sample")
    duration = float(audio.get_attribute("duration"))

    # Play
    play_sample(driver)
    ui.WebDriverWait(driver, math.ceil(duration) + 1).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )

    # Transcribe
    transcription = driver.find_element(By.TAG_NAME, "input")
    transcription.clear()
    transcription.send_keys("This is a transcription")

    # Validate
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(sleep_duration)
    click(driver, submit)


def test_init_form(driver):
    # Fill gender
    cur_gender = random.choice(["Male", "Female"])  # , "Other"])
    gender = ui.Select(driver.find_element(By.ID, "gender"))
    gender.select_by_visible_text(cur_gender)

    # Fill age
    ages = [
        "Under 20",
        "20 - 29",
        "30 - 39",
        "40 - 49",
        "50 - 59",
        "60 - 69",
        "70 - 79",
        "80 or over",
    ]
    age = ui.Select(driver.find_element(By.ID, "age"))
    age.select_by_visible_text(random.choice(ages))

    # Language related questions
    english_native_answers = ["Yes", "No"]
    english_native_answer = random.choice(english_native_answers)
    english_native = ui.Select(driver.find_element(By.ID, "english_native"))
    english_native.select_by_visible_text(english_native_answer)

    try:
        ui.WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.ID, "english_dialect_div"))
        )
        english_dialect_answers = [
            "Australian",
            "Indian/Pakistani",
            "UK",
            "US",
            "Other",
        ]
        english_dialect_answer = random.choice(english_dialect_answers)
        english_dialect = ui.Select(driver.find_element(By.ID, "english_dialect"))
        english_dialect.select_by_visible_text(english_dialect_answer)

    except Exception:
        ui.WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.ID, "native_language_div"))
        )

        native_language_answers = ["French", "English", "Bulgarian", "German"]
        native_language = driver.find_element(By.ID, "native_language")
        native_language.clear()
        native_language.send_keys(
            random.choice(native_language_answers)
        )  # TODO: Random

        english_levels = [
            "Bilingual",
            "Advanced",
            "Intermediate",
            "Elementary",
        ]
        english_level = ui.Select(driver.find_element(By.ID, "english_level"))
        english_level.select_by_visible_text(random.choice(english_levels))

    # Select the fact that we are using headphones

    click(driver, driver.find_element(By.ID, "using_headphones"))

    # Select headphone model
    headphones_model = driver.find_element(By.ID, "headphones_model")
    headphones_model.clear()
    headphones_model.send_keys("Bose QuietComfort 35")  # TODO: Random

    # Validate
    ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(20)
    click(driver, submit)


def test_feedback_form(driver):

    # Environment
    same_environment_answers = ["Yes", "No"]
    same_environment_answer = random.choice(same_environment_answers)
    same_environment = ui.Select(driver.find_element(By.ID, "same_environment"))
    same_environment.select_by_visible_text(same_environment_answer)

    environments = [
        "Quiet all the time",
        "Quiet most of the time",
        "Equally quiet and noisy",
        "Noisy most of the time",
        "Noisy all the time",
    ]
    environment = ui.Select(driver.find_element(By.ID, "environment"))
    environment.select_by_visible_text(random.choice(environments))

    # TTS
    tts_worker_answers = ["Yes", "No"]
    tts_worker_answer = tts_worker_answers[
        1
    ]  # random.choice(tts_worker_answers)
    tts_worker = ui.Select(
        driver.find_element(By.ID, "tts_worker")
    )
    tts_worker.select_by_visible_text(tts_worker_answer)

    speech_science_worker_answers = ["Yes", "No"]
    speech_science_worker_answer = speech_science_worker_answers[
        1
    ]  # random.choice(speech_science_worker_answers)
    speech_science_worker = ui.Select(
        driver.find_element(By.ID, "speech_science_worker")
    )
    speech_science_worker.select_by_visible_text(speech_science_worker_answer)

    tts_familiaritys = [
        "Every day",
        "Once a week",
        "Once a month",
        "A few times a year",
        "A few times ever",
        "Never",
        "I'm not sure",
    ]
    tts_familiarity = ui.Select(driver.find_element(By.ID, "tts_familiarity"))
    tts_familiarity.select_by_visible_text(random.choice(tts_familiaritys))


    participated_blizzard_answers = ["Yes", "No"]
    participated_blizzard_answer = participated_blizzard_answers[
        1
    ]  # random.choice(participated_blizzard_answers)
    participated_blizzard = ui.Select(
        driver.find_element(By.ID, "participated_blizzard")
    )
    participated_blizzard.select_by_visible_text(participated_blizzard_answer)

    # Feel free form feedback
    freeform_feedback = driver.find_element(By.ID, "freeform_feedback")
    freeform_feedback.clear()
    freeform_feedback.send_keys(str(driver))

    # Validate
    ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(20)
    click(driver, submit)


def test_register(driver, rand_id):
    global logger

    # Fill email
    email = driver.find_element(By.ID, "email")
    logger.info(f'Starting the test by being the user "{rand_id}@tcd.ie"')
    email.clear()
    # email.send_keys(f"{rand_id}@tcd.ie")
    safe_send_keys(driver, "email", f"{rand_id}@tcd.ie", By.ID)

    # Validate legal
    legalterms_check = driver.find_element(By.ID, "legalterms")
    click(driver, legalterms_check)

    # Validate
    ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
    submit = driver.find_element(By.ID, "submit")
    sleep_wrapper(10)
    click(driver, submit)


def run_test(driver, rand_id, url="http://localhost:8080/"):
    global logger
    driver.get(url)

    logger.info("Start the test.")

    # Register
    test_register(driver, rand_id)
    driver.implicitly_wait(10)
    sleep_wrapper(30)

    # Fill Profile
    test_init_form(driver)
    sleep_wrapper(30)

    # Core of the test
    tests = [
        # Similarity
        ("Intro_Similarity", "novel", test_similarity_step, 1, 4),
        ("Similarity", "novel", test_similarity_step, 8, 4),

        # Naturalness
        ("Intro_MOS", "novel", test_mos_step, 1, 4),
        ("Naturalness", "novel", test_mos_step, 8, 4),
        ("Naturalness", "news", test_mos_step, 8, 4),
        ("Naturalness", "novel", test_mos_step, 8, 4),
        ("Naturalness", "news", test_mos_step, 7, 4),

        # # Intelligibility
        # ("Intro_Intelligibility", "sus", test_intel_step, 1, 20),
        # ("Intelligibility", "sus", test_intel_step, 7, 20),
        # ("Intelligibility", "sus", test_intel_step, 7, 20),
    ]
    for i_section, cur_section in enumerate(tests, 1):
        (type_test, type_utt, test_func, nb_steps, sleep_duration) = cur_section
        logger.info(
            f'Starting the section {i_section} which is a "{type_test}" on utterances of type "{type_utt}" with {nb_steps} steps'
        )
        for i_step in range(1, nb_steps + 1):
            logger.debug(f" - step {i_step}/{nb_steps}")
            test_func(driver, sleep_duration)

            # wait to move to the next
            driver.implicitly_wait(1)  # seconds
            sleep_wrapper(3)

    # Fill the feedbacks
    test_feedback_form(driver)
    # sleep_wrapper(30)


def instanciate_driver(browser="chromium"):
    if browser == "chromium":
        s = Service("./chromedriver")
        opt = webdriver.ChromeOptions()
        opt.add_argument("--mute-audio")
        # opt.add_argument('headless');
        return webdriver.Chrome(service=s, options=opt)

    if browser == "firefox":
        s = Service("./geckodriver")
        profile = webdriver.FirefoxProfile()
        profile.set_preference("media.volume_scale", "0.0")
        profile.set_preference("media.eme.enabled", True)
        profile.update_preferences()
        return webdriver.Firefox(service=s, firefox_profile=profile)

    if browser == "safari":
        return webdriver.Safari()

    if browser == "opera":
        return webdriver.Opera(executable_path="./operadriver")

    if browser == "edge":
        s = Service("./msedgedriver.exe")
        return webdriver.Edge(service=s)

    raise Exception(f"{browser} is not a valid, select a proper browser!")


def test_wrapper(args):
    (browser, url) = args

    # Generate the ID
    rand_id = random.randint(0, 99999999)

    # create logger and formatter
    logger = logging.getLogger(f"{__name__} ({rand_id})")

    # Run the test
    driver = instanciate_driver(browser)
    try:
        start = time.time()
        run_test(driver, rand_id, url)
        end = time.time()
        elapsed = end - start
        logger.info(f"End of the test - elapsed time = {elapsed}")
        sleep_wrapper(1)
    except Exception as ex:
        raise ex
        logger.error(f"Had to stop {rand_id} because of Exception {type(ex)}: {ex}")
    finally:
        driver.quit()


###############################################################################
#  Envelopping
###############################################################################
if __name__ == "__main__":
    # Initialization
    arg_parser = define_argument_parser()
    args = arg_parser.parse_args()
    logger = configure_logger(args)

    if args.nb_procs == 1:
        test_wrapper((args.browser, args.url))
    elif args.nb_procs > 1:
        with Pool(args.nb_procs) as p:
            p.map(test_wrapper, [(args.browser, args.url)] * args.nb_procs)
    else:
        logger.error(f"The number of processes ({args.nb_procs}) should be >= 1")
        sys.exit(-1)
