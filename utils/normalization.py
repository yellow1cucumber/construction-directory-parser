from typing import List
from core.sitemap_extraction.article import Article
from core.sitemap_extraction.category import Category
from core.sitemap_extraction.sitemap import SiteMap

def normalize_sitemap(site_map: SiteMap) -> SiteMap:
    """
    Normalizes a SiteMap object by converting empty categories (categories
    without subcategories and articles) into articles and removing them
    from their parent's list of subcategories.

    Args:
        site_map (SiteMap): The SiteMap object to normalize.

    Returns:
        SiteMap: The normalized SiteMap object.
    """

    def normalize_category(target_categories: List[Category], parent_category: Category):
        """
        Recursively normalizes categories by:
        1. Converting categories without subcategories and articles into articles.
        2. Removing the converted categories from their parent's list of subcategories.
        3. Recursively processing subcategories.

        Args:
            target_categories (List[Category]): The list of categories to process.
            parent_category (Category): The parent category containing the target categories.
        """
        # Iterate over a copy of the list to avoid modifying the list during iteration
        for category in target_categories[:]:
            # If the category has no subcategories and no articles, treat it as an article
            if not category.subcategories and not category.articles:
                parent_category.articles.append(
                    Article(
                        title=category.name,  # Use the category name as the article title
                        url=category.url,     # Use the category URL as the article URL
                        html=''               # Empty HTML content for the article
                    )
                )
                # Remove the now-converted category from the list of subcategories
                target_categories.remove(category)
            else:
                # Recursively process subcategories
                normalize_category(category.subcategories, category)

    # Process the root categories of the SiteMap
    for root_category in site_map.categories:
        normalize_category(root_category.subcategories, root_category)

    return site_map
