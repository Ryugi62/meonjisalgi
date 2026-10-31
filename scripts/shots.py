import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":720,"height":900}, device_scale_factor=2, locale="ko-KR")
    pg.goto("https://meonjisalgi.vercel.app/", wait_until="networkidle")
    pg.select_option("#region","경남"); pg.fill("#endYm","2025-03"); pg.click("#go")
    pg.wait_for_selector(".item",timeout=90000); time.sleep(1)
    pg.evaluate("document.querySelectorAll('.item details summary')[1].click()")
    pg.evaluate("window.scrollTo(0,330)"); time.sleep(.5); pg.screenshot(path="assets/s1.png")
    pg.select_option("#region","서울"); pg.fill("#qs","서울 강남구는 정착금을 더 주나요?"); pg.click("#ask")
    pg.wait_for_function("document.querySelector('#ans .item, #ans .hold, #ans .err')",timeout=90000)
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); time.sleep(.5); pg.screenshot(path="assets/s2.png")
    pg.select_option("#region","부산"); pg.fill("#qs","부산 정착금이 700만원 맞나요?"); pg.click("#ask"); time.sleep(1)
    pg.wait_for_function("document.querySelector('#ans .item, #ans .hold, #ans .err')",timeout=90000)
    pg.evaluate("document.querySelector('#ans details summary')&&document.querySelector('#ans details summary').click()")
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); time.sleep(.5); pg.screenshot(path="assets/s3.png")
    b.close()
