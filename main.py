import os
import zipfile
import tarfile
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

end_ch = None
ch_name_g = None

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
    print(f"{start}=============")
    try:
        int_url = start.split("/")[3::]
        start = "/".join(int_url)
        chapter_list.append(start)
    except:
        url_list = driver.find_elements(
            By.XPATH,
            f"//div[@class='grow grid gap-3 grid-cols-2 lg:grid-cols-6']//optgroup[@label='Chapters']/option",
        )

        for url in url_list:
            link = url.get_attribute("value")
            chapter_list.append(link)

        global end_ch
        end_ch = len(chapter_list)
        start_index = chapter_list[start]

    vol_pattern = fr"vol-\d+-ch-"

    for ch in chapter_list:
        if f"ch-{start}" in ch or f"chapter-{start}" in ch or f"{vol_pattern}{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-0{start}" in ch or f"chapter-0{start}" in ch or f"{vol_pattern}0{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-00{start}" in ch or f"chapter-00{start}" in ch or f"{vol_pattern}00{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        elif f"ch-000{start}" in ch or f"chapter-000{start}" in ch or f"{vol_pattern}000{start}" in ch:
            first_url = ch
            start_index = chapter_list.index(first_url)
            break
        else:
            start_index = 0


    # chapter_links_list = chapter_list[start_index::]
    if end is not None:
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

        # Name the chapter acording to the name of the link 
        # [ch, chapter, vol+(volnum)+ch, side+story]
        name_ = page.split("/")[-1].split("-")
        if name_[1] == "ch":
            name_ = name_[2::]
            name_ = ".".join(name_)

        elif name_[1] == "chapter":
            name_ = name_[2::]
            name_ = ".".join(name_)

        elif name_[1] == "vol":
            name_ = name_[4::]
            name_ = ".".join(name_)

        elif name_[1] == "side":
            name_ = name_[3::]
            name_ = ".".join(name_)

        else:
            name_ = ".".join(name_)

        try:
            name_ = name_.split(":")[0]
        except:
            name_ = name_


        urls = get_urls(driver)
        url_lists[name_] = urls

    driver.quit()

    # add placeholders[0] for the chapter name[dir name]
    for name in url_lists.keys():
        url_list = url_lists[name]

        if "." not in name:
            ch_name = f"{int(name):04d}"
        # elif "." in name:
        #     try:
        #         temp_name = name.split(".")[0]
        #         ch_name = f"{int(temp_name):04d}"
        #     except:
        #         try:
        #             temp_name = name.split(".")[1]
        #             ch_name = f"{int(temp_name):04d}"
        #         except:
        #             ch_name = name
        else:
            ch_name = name

        os.makedirs(str(ch_name))
        global ch_name_g
        ch_name_g = int(ch_name)
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
def initial_user_choice(manga_url, start_chapter, end_chapter):

    while True:
        print("Enter your choice (1 or 2):")
        number_choice = input().strip()
        try:
            number_choice = int(number_choice)
            break
        except:
            print("That's not a valid number. Please try again.")

    if number_choice == 1:
        print("================================================================================")
        print("NOTE THE PROGRAM CAN NOT DOWNLOAD ANY CHAPTER WITH THE TAG 'SIDESTORY'")
        print("================================================================================")

        while True:
            print("1- Enter chapter URL")
            print("2- Enter chapter number")
            chapter_inf = input().strip()
            
            if chapter_inf == "1":
                print("Enter chapter URL:")
                start_chapter = input().strip()
                if "/" in start_chapter:
                    break
            elif chapter_inf == "2":
                while True:
                    print("Enter chapter number:")
                    start_chapter = input().strip()
                    try:
                        start_chapter = int(start_chapter)
                        break
                    except:
                        print("That's not a valid number. Please try again.")
                break



        main(manga_url, start_chapter, end_chapter)
        return [start_chapter]

    elif number_choice == 2:
        print("================================================================================")
        print("NOTE THE PROGRAM CAN NOT NAME ANY CHAPTER WITH THE TAG 'SIDESTORY'")
        print("================================================================================")

        while True:
            print("Enter start chapter number:")
            start_chapter = input().strip()
            try:
                start_chapter = int(start_chapter)
                break
            except:
                print("That's not a valid number. Please try again.")
        while True:
            print("Enter end chapter[0 all]:")
            end_chapter = input().strip()
            try:
                end_chapter = int(end_chapter)
                break
            except:
                print("That's not a valid number. Please try again.")

        main(manga_url, start_chapter, end_chapter)
        return[start_chapter, end_chapter]

    else:

        print("please enter a valid number !!!")
        initial_user_choice(manga_url, start_chapter, end_chapter)


def start_server():
    print("start server [Y-N]:")
    option = input().strip().lower()
    if option == 'y':
        try:
            os.system("python -m http.server")
        except Exception as e:
            print(f"An error occurred: {e}")
    elif option == 'n':
        return
    else:
        print("Enter a valid answer!!!")
        start_server()



def create_tar(start_, end_):
    n_1 = random.randint(1, 2000)
    n_2 = random.randint(1, 2000)
    n_3 = random.randint(1, 2000)
    n_4 = random.randint(1, 2000)

    while True:
        print("turn to tar[Y-N]:")
        tar_choice = input().strip().lower()
        if tar_choice == "y":
            while True:
                print("remove all .cbz after the .tar created[Y-N]:")
                clean_choice = input().strip().lower()
                if clean_choice == 'y':
                    with tarfile.open(f"{n_1}{n_2}{n_3}{n_4}.tar", 'w') as tarf:
                        for i in range(int(start_), int(end_) + 1):
                            prefix = f"{i:04}.cbz"
                            tarf.add(f"{prefix}")
                            os.remove(prefix)
                    return
                elif clean_choice == 'n':
                    with tarfile.open(f"{n_1}{n_2}{n_3}{n_4}.tar", 'w') as tarf:
                        for i in range(int(start_), int(end_) + 1):
                            prefix = f"{i:04}.cbz"
                            tarf.add(f"{prefix}")
                    return
                else:
                    print("not a valid answer!!!")
        elif tar_choice == "n":
            return
        else:
            print("not a valid answer!!!")




def create_zip(start_, end_):
    if end_ is not None and end_ != start_:
        while True:
            print("turn to cbz[Y-N]:")
            zip_choice = input().strip().lower()
            if zip_choice == "y":
                    for i in range(int(start_), int(end_) + 1):
                        prefix = f"{i:04}"
                        for dir_name in os.listdir():
                            if dir_name.startswith(prefix) and os.path.isdir(dir_name):
                                zip_name = f"{dir_name}.cbz"
                                with zipfile.ZipFile(zip_name, 'w') as zipf:
                                    for root, _, files in os.walk(dir_name):
                                        files.sort()
                                        for file in files:
                                            zipf.write(os.path.join(root, file), arcname=file)
                                os.rename(zip_name, os.path.join(zip_name))
                    create_tar(start_, end_)
                    return
            elif zip_choice == "n":
                return
            else:
                print("not a valid answer!!!")
    else:
        prefix = f"{ch_name_g:04d}"
        for dir_name in os.listdir():
            if dir_name.startswith(prefix) and os.path.isdir(dir_name):
                zip_name = f"{dir_name}.cbz"
                with zipfile.ZipFile(zip_name, 'w') as zipf:
                    for root, _, files in os.walk(dir_name):
                        files.sort()
                        for file in files:
                            zipf.write(os.path.join(root, file), arcname=file)
                os.rename(zip_name, os.path.join(zip_name))
                return


# handel the after download 
def after_first_choice(start, end):
    try:
        start_ = f"{start:04d}"
    except:
        start_ = f"{ch_name_g:04d}"

    if end == 0:
        end_ = f"{end_ch:04d}"
    elif type(end) is str and "/" in end:
        end_ = None
    else:
        end_ = f"{end:04d}"

    while True:
        if end_ is not None and end_ != start_:
            print("continue (zip the files) (turn the files into '.tar') [Y-N]:")
        else:
            print("turn to cbz[Y-N]::")
        continue_choice = input().strip().lower()
        if continue_choice == "y":
            create_zip(start_, end_)
            break
        elif continue_choice == "n":
            return
        else:
            print("enter a valid answer!!!")


if __name__ == "__main__":
    start_chapter = None
    end_chapter = None
    print("Enter a URL like 'https://mangapark.net/title/id/name/c1-en'\nURL:")
    manga_url = input().strip()
    print("1. One chapter")
    print("2. Multiple chapters")

    cha = initial_user_choice(manga_url, start_chapter, end_chapter)
    start = cha[0]
    try:
        end = cha[1]
    except:
        end = cha[0]
    after_first_choice(start, end)
