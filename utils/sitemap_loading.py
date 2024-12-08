from core.sitemap_extraction.sitemapExtractor import SiteMapExtractor, ExtractorOptions
from core.sitemap_extraction.sitemap import SiteMap


def request_sitemap(options: ExtractorOptions) -> SiteMap:
    """
    Loads a sitemap from the URL specified in the options.

    Args:
        options (ExtractorOptions): Configuration settings for the `SiteMapExtractor`.

    Returns:
        SiteMap: The extracted sitemap.
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.extract_site_map()
    return sitemap


def request_sitemap_and_export(options: ExtractorOptions, file_name: str) -> SiteMap:
    """
    Loads a sitemap from the URL specified in the options and exports it to a JSON file.

    Args:
        options (ExtractorOptions): Configuration settings for the `SiteMapExtractor`.
        file_name (str): The name of the file to export the sitemap to.

    Returns:
        SiteMap: The extracted sitemap.
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.extract_site_map()
    map_extractor.export_results(sitemap, file_name)
    return sitemap


def import_sitemap_from_json_file(options: ExtractorOptions, file_name: str) -> SiteMap:
    """
    Imports a sitemap from a specified JSON file.

    Args:
        options (ExtractorOptions): Configuration settings for the `SiteMapExtractor`.
        file_name (str): The name of the file to import the sitemap from.

    Returns:
        SiteMap: The imported sitemap.
    """
    map_extractor = SiteMapExtractor(options)
    sitemap: SiteMap = map_extractor.load_site_map_from_json(file_name)
    return sitemap
