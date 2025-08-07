from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.firefox.launch()
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://books.toscrape.com/")
    print("On the landing page")
    page.screenshot(path="screenshots/00-landing_page.png")

    page.get_by_role("link", name="Travel", exact=True).click()
    print("<Travel> Clicked")
    page.screenshot(path="screenshots/01-travel.png")

    book_info = {
            "upc": [],
            "title": [],
            "price_excl_tax": [],
            "price_incl_tax": [],
            "stars": [],
            "num_reviews": [],
            "availability": []
            }
    books_articles = page.locator("ol.row li")
    books_articles_count = books_articles.count()
    print(f"The number of books on <Travel> is: {books_articles_count}")
    for nth in range(books_articles_count):
        books_articles.nth(nth).locator("h3 a").click()
        print(f"Book {nth + 1} Clicked")
        page.screenshot(path=f"screenshots/{(nth + 2):>02}-book{nth + 1}.png")

        title = page.locator(".product_main h1").inner_text()
        book_info["title"].append(title)
        print(f"\ttitle: {title}")

        stars_class = page.locator(".product_main p.star-rating").get_attribute("class")
        stars = stars_class.split()[1]
        book_info["stars"].append(stars)
        print(f"\tstarts: {stars}")

        info_table = page.locator(".table-striped")

        upc_tr = info_table.locator("tr").filter(has_text="UPC")
        upc = upc_tr.locator("td").inner_text()
        book_info["upc"].append(upc)
        print(f"\tupc: {book_info["upc"][nth]}")

        price_excl_tax_tr = info_table.locator("tr").filter(has_text="Price (excl. tax)")
        price_excl_tax = price_excl_tax_tr.locator("td").inner_text()
        book_info["price_excl_tax"].append(price_excl_tax)
        print(f"\tprice_excl_tax: {book_info["price_excl_tax"][nth]}")

        price_incl_tax_tr = info_table.locator("tr").filter(has_text="Price (incl. tax)")
        price_incl_tax = price_incl_tax_tr.locator("td").inner_text()
        book_info["price_incl_tax"].append(price_incl_tax)
        print(f"\tprice_incl_tax: {book_info["price_incl_tax"][nth]}")

        availability_tr = info_table.locator("tr").filter(has_text="Availability")
        availability = availability_tr.locator("td").inner_text()
        book_info["availability"].append(availability)
        print(f"\tavailability: {book_info["availability"][nth]}")

        num_reviews_tr = info_table.locator("tr").filter(has_text="Number of reviews")
        num_reviews = num_reviews_tr.locator("td").inner_text()
        book_info["num_reviews"].append(num_reviews)
        print(f"\tnum_reviews: {book_info["num_reviews"][nth]}")

        page.get_by_role("link", name="Travel", exact=True).click()
        print("Back To <Travel>")

    print(book_info)

