import os
import subprocess
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_urls(driver):
    time.sleep(5)
    try:
        show_all_button = driver.find_element(
            By.XPATH, "//button[@class='btn btn-sm btn-outline-info ms-1']"
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        show_all_button.click()
        time.sleep(5)
        imgs = driver.find_elements(
            By.XPATH, "//div[@id='viewer']/div/div[@class='item']/img"
        )
    except:
        imgs = driver.find_elements(
            By.XPATH, "//div[@class='flex flex-col items-center bg-base-100']/div//img"
        )
    return [img.get_attribute("src") for img in imgs]


def get_img(url, dir, name):
    extention_img = url.split(".")[-1]
    if extention_img in ["png", "jpeg", "jpg", "webp"]:
        image_path = f"{dir}/{name}.{extention_img}"
    else:
        image_path = f"{dir}/{name}.png"
    # urllib.request.urlretrieve(url, image_path)
    try:
        print("img_index", name)
        print("img_url", url)
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()

        # Save the image to the destination folder
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"--------------- {name} DONE ---------------")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        get_img(url, dir, name)

def get_pics_num(driver):
    pics_number = driver.find_element(
        By.XPATH,
        "//div[@id='viewer']/div/div[@class='text-center text-muted small text-nowrap']",
    )
    if pics_number:
        pics_number_txt = pics_number.text
        pics_num = pics_number_txt.split("/")[-1].strip()
        return pics_num


def get_chapter(driver, start, end):
    time.sleep(5)

    chapter_list = []
    url_list = driver.find_elements(
        By.XPATH,
        f"//div[@class='grow grid gap-3 grid-cols-2 lg:grid-cols-6']//optgroup[@label='Chapters']/option",
    )
    for url in url_list:
        link = url.get_attribute("value")
        chapter_list.append(link)

    start_index = chapter_list[0]
    for ch in chapter_list:
        if f"ch-{start}" in ch or f"chapter-{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-0{start}" in ch or f"chapter-0{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-00{start}" in ch or f"chapter-00{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-000{start}" in ch or f"chapter-000{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        else:
            start_index = 0


    # chapter_links_list = chapter_list[start_index::]
    if end >= 0:
        chapter_links_list = chapter_list[start_index::]
        if end == 0:
            chapter_links_list = chapter_list[start_index::]
        else:
            for ch in chapter_list:
                if f"ch-{end}" in ch or f"chapter-{end}" in ch:
                    last_url = ch
                    end_index = chapter_list.index(last_url)
                    chapter_links_list = chapter_list[start_index : end_index + 1]
                    break
                elif f"ch-0{end}" in ch or f"chapter-0{end}" in ch:
                    last_url = ch
                    end_index = chapter_list.index(last_url)
                    chapter_links_list = chapter_list[start_index : end_index + 1]
                    break
                elif f"ch-00{end}" in ch or f"chapter-00{end}" in ch:
                    last_url = ch
                    end_index = chapter_list.index(last_url)
                    chapter_links_list = chapter_list[start_index : end_index + 1]
                    break
                elif f"ch-000{end}" in ch or f"chapter-000{end}" in ch:
                    last_url = ch
                    end_index = chapter_list.index(last_url)
                    chapter_links_list = chapter_list[start_index : end_index + 1]
                    break
                else:
                    chapter_links_list = chapter_list[start_index::]


        return chapter_links_list

    else:
        return [chapter_list[start_index]]


def get_setting(driver):
    driver.get("https://mangapark.net/site-settings?group=safeBrowsing")
    time.sleep(3)
    setting_btn = driver.find_element(
        By.XPATH,
        "//label/input[@class='radio checked:bg-error']",
    )
    setting_btn.click()
    time.sleep(3)


def main(url, start, end):
    url_lists = {}
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(options=chrome_options)
    get_setting(driver)
    driver.get(url)
    time.sleep(2)
    chapter_list = get_chapter(driver, start, end)
    for page in chapter_list:
        driver.get(f"https://mangapark.net/{page}")
        name_ = page.split("/")[-1].split("-")[2::]
        name_ = ".".join(name_)
        urls = get_urls(driver)
        url_lists[name_] = urls

    driver.quit()
    for name in url_lists.keys():
        url_list = url_lists[name]
        if "." not in name:
            ch_name = f"{int(name):04d}"
        # elif "." in name:
            # temp_name = name.split(".")[0]
            # ch_name = f"{int(temp_name):03}"
        else:
            ch_name = name
        os.makedirs(str(ch_name))
        print(f"############### START CHAPTER {name} ###############")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                    executor.submit(get_img, url_, ch_name, f"{index:03d}")
                for index, url_ in enumerate(url_list, start=1)
            ]
            for future in as_completed(futures):
                try:
                    future.result()  # Get the result to raise any exceptions encountered
                except Exception as e:
                    print(f"Error during download: {e}")

# handel the user initial choise of the number ofchapters
def initial_user_choice(manga_url, number_choice, start_chapter, end_chapter):
    if number_choice == 1:
        start_chapter = int(input("Enter chapter number: "))
        main(manga_url, start_chapter, end_chapter)
        return [start_chapter]
    elif number_choice == 2:
        start_chapter = int(input("Enter start chapter: "))
        end_chapter = int(input("Enter end chapter[0 all]: "))
        main(manga_url, start_chapter, end_chapter)
        return[start_chapter, end_chapter]
    else:
        print("please enter a valid number !!!")
        initial_user_choice(manga_url, number_choice, start_chapter, end_chapter)


def start_server():
    option = input("start server[Y-N]: ").lower()
    if option == 'y':
        os.system("python -m http.server")
    elif option == 'n':
        return
    else:
        print("enter a valid answer!!!")
        start_server()


def clear(dir_name, start_, end_):
    clear_option = input("do you want to delete every thing not the .tar [Y-N]: ").lower()
    if clear_option == 'y':
        os.system(f"$(for i in {{{start_}..{end_}}};do rm -rf $i;done)")
        os.system(f"rm -rf '{dir_name}'")
        start_server()
        return
    elif clear_option == 'n':
        return
    else:
        print("enter a valid answer!!!")
        clear(dir_name, start_, end_)


def create_tar(dir_name, start_, end_):
    while True:
        tar_choice = input("turn to tar[Y-N]: ").lower()
        if tar_choice == "y":
            if os.path.isfile(f"'{dir_name}.tar'"):
                os.system(f"rm -rf '{dir_name}.tar'")
            command_2 = f"tar -cf '{dir_name}.tar' '{dir_name}'"
            subprocess.run(command_2, shell=True, capture_output=True, text=True)
            clear(dir_name, start_, end_)
            return
        elif tar_choice == "n":
            return
        else:
            print("not a valid answer!!!")


def create_zip(start_, end_):
    while True:
        zip_choice = input("turn to cbz[Y-N]: ").lower()
        if zip_choice == "y":
            print("enter the name of the manga:")
            dir_name = input("")
            dir_name = dir_name.replace(" ", "_")

            if os.path.isdir(dir_name):
                pass
            else:
                os.system(f"mkdir '{dir_name}'")
            command_1 = f"for i in {{{start_}..{end_}}}; do zip $i.cbz $i/*; done && mv *.cbz '{dir_name}'"
            subprocess.run(command_1, shell=True, capture_output=True, text=True)
            create_tar(dir_name, start_, end_)
            return
        elif zip_choice == "n":
            return
        else:
            print("not a valid answer!!!")


# handel the after download 
def after_first_choice(start, end):
    start_ = f"{start:04d}"
    end_ = f"{end:04d}"
    while True:
        continue_choice = input("continue[Y-N]: ").lower()
        if continue_choice == "y":
            create_zip(start_, end_)
            break
        elif continue_choice == "n":
            return
        else:
            print("enter a valid answer!!!")


# if __name__ == "__main__":
def start():
    start_chapter = None
    end_chapter = None
    manga_url = input("Enter a URL like 'https://mangapark.net/title/id/name/c1-en'\nURL: ")
    print("1. One chapter")
    print("2. Multiple chapters")
    number_choice = int(input("Enter your choice (1 or 2): "))
    cha = initial_user_choice(manga_url, number_choice, start_chapter, end_chapter)
    start = cha[0]
    try:
        end = cha[1]
    except:
        end = cha[0]
    after_first_choice(start, end)
