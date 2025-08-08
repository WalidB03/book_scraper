from playwright.sync_api import sync_playwright, expect
import logging

format = "[%(asctime)s - %(name)s - %(levelname)s]\t%(message)s"
logging.basicConfig(level=logging.DEBUG, format=format)
def set_logger(name, level, format, prop=False, file=None, file_mode="a"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = prop
    if file:
        handler = logging.FileHandler(file, mode=file_mode)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    return logger

debug_log = set_logger("debug_log", logging.DEBUG, format=format)
network_log = set_logger("network_log", logging.DEBUG, format=format, prop=True, file="logs/network.log", file_mode="w")
error_log = set_logger("error_log", logging.ERROR, format=format, prop=True, file="logs/error.log", file_mode="w")

def get_table_data(text, table, debug_log=debug_log):
    data_tr = info_table.locator("tr", has_text=text)
    data = data_tr.locator("td").inner_text()
    debug_log.debug(f"\t{text}: {data}")
    return data

with sync_playwright() as p:
    browser = p.firefox.launch()
    context = browser.new_context()
    page = context.new_page()
    page.on("request", lambda req: network_log.info(f"REQ: {req.method} {req.url}"))
    page.on("response", lambda res: network_log.info(f"RES: {res.status} {res.url}"))

    try:
        page_num = 1
        step = f"page{page_num:>02}"
        network_log.debug(step)
        page.goto("https://books.toscrape.com/catalogue/page-1.html")
        debug_log.debug(f"On {step}")

        while True:
            next = page.locator("li.next a")
            if not next.is_visible():
                next = None

            books_loc = page.locator("ol.row li")
            books_count = books_loc.count()
            debug_log.debug(f"books count: {books_count}")

            books = []
            for n in range(books_count):
                step = f"page{page_num:>02}_book{(n + 1):>02}"
                network_log.debug(step)
                books_loc.nth(n).locator("h3 a").click()
                debug_log.debug(f"On: {step}")

                category = page.locator("ul.breadcrumb > li:nth-of-type(3)").inner_text()
                debug_log.debug(f"\tcategory: {category}")

                title = page.locator(".product_main h1").inner_text()
                debug_log.debug(f"\ttitle: {title}")

                stars_class = page.locator(".product_main p.star-rating").get_attribute("class")
                stars = stars_class.split()[1]
                debug_log.debug(f"\tstars: {stars}")

                info_table = page.locator(".table-striped")
                upc = get_table_data("UPC", info_table)
                price_excl_tax = get_table_data("Price (excl. tax)", info_table)
                price_incl_tax = get_table_data("Price (incl. tax)", info_table)
                availability = get_table_data("Availability", info_table)
                num_reviews = get_table_data("Number of reviews", info_table)

                books.append({
                    "upc"           : upc,
                    "title"         : title,
                    "category"      : category,
                    "availability"  : availability,
                    "price_excl_tax": price_excl_tax,
                    "price_incl_tax": price_incl_tax,
                    "stars"         : stars,
                    "num_review"    : num_reviews
                })

                step = f"page{page_num:>02}"
                network_log.debug(step)
                page.go_back()
                debug_log.debug(f"On: {step}")

            if next:
                page_num += 1
                step = f"page{page_num:>02}"
                network_log.debug(step)
                next.click()
                debug_log.debug(f"On {step}")
            else:
                break

        print(books)

    except Exception as e:
        error_log.exception(step)
        page.screenshot(path=f"logs/error_{step}.png", full_page=True)

