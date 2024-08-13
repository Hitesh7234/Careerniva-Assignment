import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from time import sleep
from talentedge.items import CourseItem

class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["talentedge.com"]
    start_urls = ["https://talentedge.com/browse-courses"]

    def __init__(self, *args, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Uncomment for headless mode
        self.driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)

    def start_requests(self):
        for url in self.start_urls:
            self.driver.get(url)
            html_content = self.driver.page_source
            response = HtmlResponse(url=self.driver.current_url, body=html_content, encoding='utf-8')
            yield from self.parse_pages(response)
            yield from self.scroll_and_collect_pages()

    def scroll_and_collect_pages(self):
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # Wait for new content to load
            
            try:
                # Click the "Next" button
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='cpage-link cpage-navbtn']/img[@alt='Next']"))
                )
                ActionChains(self.driver).move_to_element(next_button).click(next_button).perform()
                sleep(2)  # Wait for the page to load
            except Exception as e:
                # If no more pages are left, break the loop
                self.logger.info("No more pages to load.")
                break

            html_content = self.driver.page_source
            response = HtmlResponse(url=self.driver.current_url, body=html_content, encoding='utf-8')
            yield from self.parse_pages(response)

    def parse_pages(self, response):
        pages = response.xpath("//div[@class='know-more-p']/a")
        for page in pages:
            url = page.xpath('@href').get()
            yield scrapy.Request(url, callback=self.parse_courses)

    def parse_courses(self, response):
        item = CourseItem()

        item['course_link'] = response.url
        item['title'] = response.xpath("//h1[@class='pl-title']/text()").get()
        item['description'] = response.xpath("normalize-space(//div[@class='desc_less']/p/text())").get()
        item['duration'] = response.xpath("//div[@class='duration-of-course']/ul/li[1]/p[1]/strong/text()").get()
        item['course_start_date'] = response.xpath("//div[@class='duration-of-course']/ul/li[2]/p/strong/text()").get()
        item['what_you_will_learn'] = " | ".join(response.xpath("//div[@class='pl-deeper-undstnd to_flex_ul']/ul/li/text()").getall()[:-2])
        item['skills'] = " | ".join(response.xpath("//div[@class='key-skills-sec']/ul/li/text()").getall())
        item['target_students'] = response.xpath("normalize-space(//div[@class='cs-card d-flex'][1]/div[2]/h4/text())").get()
        item['prerequisites'] = " | ".join(response.xpath("//div[@class='eligible-right-top-list']/ul[2]/li/text()").getall())
        item['content'] = "\n".join([f"{idx + 1}. {ele.strip()}" for idx, ele in enumerate(response.xpath("//ul[@class='nav nav-tabs syl-ul']/li/a/text()").getall())])

        faculties = response.xpath("//div[@class='facutly-card']")
        faculties_data = []

        for faculty in faculties:
            name = faculty.xpath("normalize-space(div[@class='best-fdetail']/h4/text())").get()
            designation = faculty.xpath("normalize-space(div[@class='best-fdetail']/p/text())").get()
            desc_raw = faculty.xpath("//a[@class='showFacultyDescription']/@data-description").get()
            description = html.fromstring(desc_raw).xpath('//p')
            description = [ele.text_content() for ele in description]
            faculties_data.append({
                "name": name,
                "designation": designation,
                "description": ".".join(description)
            })

        max_faculty = len(faculties)
        needed = 2 - max_faculty
        while needed > 0:
            faculties_data.append({"name": "", "designation": "", "description": ""})
            needed -= 1

        item['faculty_1_name'] = faculties_data[0]["name"]
        item['faculty_1_designation'] = faculties_data[0]["designation"]
        item['faculty_1_description'] = faculties_data[0]["description"]
        item['faculty_2_name'] = faculties_data[1]["name"]
        item['faculty_2_designation'] = faculties_data[1]["designation"]
        item['faculty_2_description'] = faculties_data[1]["description"]

        item['institute'] = response.xpath("//h5[@class='pc-name']/ol/li/a/text()").get()
        item['fee_in_inr'] = response.xpath("normalize-space(//div[@class='program-details-total-pay-amt d-flex align-items-center justify-content-between ruppes']/div[@class='program-details-total-pay-amt-right']/text())").get()
        item['fee_in_usd'] = response.xpath("normalize-space(//div[@class='program-details-total-pay-amt d-flex align-items-center justify-content-between dolor']/div[@class='program-details-total-pay-amt-right']/text())").get()

        yield item

    def close(self, reason):
        self.driver.quit()
