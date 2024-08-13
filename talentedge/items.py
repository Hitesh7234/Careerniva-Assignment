# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CourseItem(scrapy.Item):
    course_link = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    duration = scrapy.Field()
    course_start_date = scrapy.Field()
    what_you_will_learn = scrapy.Field()
    skills = scrapy.Field()
    target_students = scrapy.Field()
    prerequisites = scrapy.Field()
    content = scrapy.Field()
    faculty_1_name = scrapy.Field()
    faculty_1_designation = scrapy.Field()
    faculty_1_description = scrapy.Field()
    faculty_2_name = scrapy.Field()
    faculty_2_designation = scrapy.Field()
    faculty_2_description = scrapy.Field()
    institute = scrapy.Field()
    fee_in_inr = scrapy.Field()
    fee_in_usd = scrapy.Field()
