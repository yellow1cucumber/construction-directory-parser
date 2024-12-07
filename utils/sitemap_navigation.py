from core.extraction.article import Article
from core.extraction.category import Category
from core.extraction.sitemap import SiteMap


def find_page_by_id(site_map: SiteMap, suffix_number: int) -> Article | Category | None:
    """
    Searches for an article or category in the `SiteMap` whose URL ends with the specified number.

    This function performs a recursive search through the categories and their subcategories, as well as their associated articles.

    Args:
        site_map (SiteMap): The `SiteMap` object to search within.
        suffix_number (int): The number that the URL should end with.

    Returns:
        Article | Category | None:
            - The matching `Article` or `Category` object if found.
            - `None` if no matching item is found.

    Raises:
        ValueError: If the provided `site_map` does not have a `categories` attribute.
    """
    if not hasattr(site_map, 'categories'):
        raise ValueError("SiteMap object does not have 'categories' attribute.")

    suffix_str = str(suffix_number)

    def search(categories):
        for category in categories:
            # Check if the category's URL ends with the suffix
            if category.url.endswith(suffix_str):
                return category

            # Check if any article's URL in the category ends with the suffix
            for article in category.articles:
                if article.url.endswith(suffix_str):
                    return article

            # Recursively search within subcategories
            result = search(category.subcategories)
            if result:
                return result
        return None

    return search(site_map.categories)
