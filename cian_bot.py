import logging, time, os
from credentials import PHONE_WO_7, EMAIL, PASSWORD
from logging.handlers import RotatingFileHandler
from selenium.webdriver import Firefox, Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

class CianBot:

    def __init__(self):
        self.logger = logging.getLogger('CIANBOT')
        log_file = 'cian_bot.log'
        log_formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s:%(message)s')
        handler = RotatingFileHandler(log_file, mode='a', maxBytes=20*1024*1024, backupCount=60)
        handler.setFormatter(log_formatter)
        self.logger.addHandler(handler)
        
        # Для Хрома
        #useragent = UserAgent()
        #options = ChromeOptions()
        #options.add_argument('user-agent={}'.format(useragent.ie))
        #options.add_argument('--disable-blink-features=AutomationControlled')
        #options.add_argument('--no-sandbox')
        #self.browser = Chrome(executable_path='/usr/cianbot/chromedriver', service_log_path=os.path.devnull, options=options)
    
        options = Options()
        options.headless = True

        self.browser = Firefox(executable_path='/home/element/Projects/CIAN/driver', service_log_path=os.path.devnull, options=options)
        self.browser.maximize_window()
        self.logger.warning(" started to work")

    def go_to_page(self, uri):
        self.browser.get(uri)
        self.logger.warning(' visited {}'.format(uri))

    def login_phone(self, phone):

        self.browser.get('https://www.cian.ru/authenticate/')
        time.sleep(5)

        self.browser.find_element_by_xpath("//span[contains(text(), 'Войти по телефону')]").click()
        time.sleep(3)

        phone_input = self.browser.find_element_by_name('tel')        
        time.sleep(3)

        phone_input.send_keys(phone)
        time.sleep(3)

        self.browser.find_element_by_xpath("//span[contains(text(), 'Продолжить')]").click()
        time.sleep(5)

        code_input = self.browser.find_element_by_name('code')

        time.sleep(10)
    
        code = 0
        while code == 0:
            with open('code.txt', 'rt') as file:
                data = file.read()
                data_dict = eval(data)
                code = data_dict.get('CODE', 0)
                if code == 0:
                    self.logger.warning(' waiting phone code')
                time.sleep(10)

    
        code_input.send_keys(code)
        time.sleep(5)
        self.logger.warning(' logined on "https://cian.ru" by phone')

    def configure_filter(self):
        self.browser.find_element_by_xpath("//div[contains(text(), 'Любая сделка')]").click()
        self.browser.find_element_by_xpath("//div[contains(text(), 'Продать')]").click()
        time.sleep(2)

        self.browser.find_element_by_xpath("//div[contains(text(), 'Любая недвижимость')]").click()
        self.browser.find_element_by_xpath("//div[contains(text(), 'Жилая')]").click()
        time.sleep(2)

        self.browser.find_element_by_xpath("//div[contains(text(), 'Любые заявки')]").click()
        self.browser.find_elements_by_xpath("//span[text()='Собственник'][@class='f341f0ad46--label--2s_qZ']")[0].click()
        time.sleep(5)

        self.browser.find_element_by_xpath("//span[contains(text(), 'Все фильтры')]").click()
        time.sleep(5)

        city_input = self.browser.find_element_by_id('geo-suggest-input')
        city_input.clear()
        city_input.send_keys('Москва')
        time.sleep(3)

        city_input.send_keys(Keys.ENTER)
        time.sleep(3)

        price_from = self.browser.find_element_by_css_selector("input[placeholder='от']")
        price_from.clear()
        price_from.send_keys('5000000')
        time.sleep(3)

        self.browser.find_elements_by_xpath("//span[text()='Показать заявки']")[1].click()        
        time.sleep(3)    
        self.logger.warning(' configured filter for leads')

    def process_leads(self):
        time.sleep(2)
        leads = self.browser.find_elements_by_xpath("//button[@data-name='OpenLead']")

        if leads:
            for lead in leads:
                lead.click()
                time.sleep(5)
                
                windows = self.browser.window_handles
                self.browser.switch_to.window(windows[1])
                self.logger.warning(' clicked on lead - {}'.format(self.browser.current_url))
                time.sleep(2)
                
                try:
                    a = self.browser.find_element_by_xpath("//div[text()='К сожалению, эту заявку нельзя оплатить и взять в работу.']")
                    self.logger.error(" Lead can't be proccessed!")
                    self.browser.close()
                    self.browser.switch_to.window(windows[0])
                    continue
                except:
                    pass
                
                try:
                    buy_leads_btns = self.browser.find_elements_by_xpath("//button[contains(text(), 'Купить заявку')]")
                    time.sleep(3)

                    if buy_leads_btns and len(buy_leads_btns) > 1:
                        buy_leads_btns[0].click()
                        time.sleep(3)

                        self.browser.find_element_by_xpath("//button[contains(text(), 'Оплатить ')]").click()
                        self.logger.warning(' try to buy lead')
                        time.sleep(3)

                        try:
                            c = self.browser.find_element_by_xpath("//div[contains(text(), 'Недостаточно средств')]")
                            self.logger.error(' NECESSARY TO DEPOSIT MONEY ON YOUR ACCOUNT!')
                
                        except:
                            self.logger.warning(' BUYED LEAD SUCCESSFULLY! {}'.format(self.browser.current_url()))
                
                        finally:
                            self.browser.close()
                            self.browser.switch_to.window(windows[0])
                            time.sleep(2)
                        continue

                    else:
                        self.logger.warning(' Lead may be buyed many rieltors only')

                except:
                    self.logger.warning(" Lead can't be buyed")

                self.browser.close()
                self.browser.switch_to.window(windows[0])

    def login_email(self, email, password):
        self.browser.get('https://www.cian.ru')
        time.sleep(5)

        self.browser.find_element_by_xpath("//span[contains(text(), 'Войти')]").click()      
        name_input = self.browser.find_element_by_name('username')
        time.sleep(2)
        name_input.clear()
        time.sleep(2)
        name_input.send_keys(email)
        time.sleep(2)

        self.browser.find_element_by_xpath("//span[contains(text(), 'Продолжить')]").click()
        time.sleep(5)
        password_input = self.browser.find_element_by_name('password')
        time.sleep(2)
        password_input.clear()
        time.sleep(2)
        password_input.send_keys(password)
        time.sleep(2)

        self.browser.find_elements_by_xpath("//span[text()='Войти']")[-1].click()
        self.logger.warning(' logined on "https://cian.ru" by email')

    def destruct(self):
        self.browser.close()
        self.browser.quit()
        self.logger.warning(' finished to work')


if __name__ == '__main__':
    while True:
        bot = CianBot()
        try:

            while True:
                start_time = time.time()

                bot.login_email(EMAIL, PASSWORD)
                time.sleep(3)

                bot.go_to_page("https://my.cian.ru/leads")
                time.sleep(5)

                bot.configure_filter()
                time.sleep(3)

                while True:
                    try:
                        if (time.time() - start_time) < 1800:
                            bot.process_leads()
                            time.sleep(2)

                            bot.browser.find_element_by_xpath("//span[text()='Показать заявки']").click()     
                            bot.logger.warning(' refreshed leads')
                            time.sleep(3)
                        else:
                            break
                    except:
                        continue
        
                bot.browser.delete_all_cookies()
                bot.browser.refresh()
                bot.logger.warning(' COOKIES REFRESHED')
                continue

        except Exception as e:
            bot.logger.error(e)
            continue
        
        finally:
            bot.destruct()
