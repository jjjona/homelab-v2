import { load } from "cheerio";
import { logger } from "../utils/logger.js";
import { searchCacheManager } from "./search-cache.js";

const BASE_URL = process.env.LG_BASE_URL?.replace(/\/$/, "");

const languageCodes = {
    English: "en",
    German: "de",
    French: "fr",
    Spanish: "es",
    Italian: "it",
    Dutch: "nl",
    Portuguese: "pt",
};

function sizeInBytes(text) {
    const match = text.match(/^([\d.]+)\s*([KMGT]?B)$/i);
    if (!match)
        return undefined;
    const powers = { B: 0, KB: 1, MB: 2, GB: 3, TB: 4 };
    return Math.round(parseFloat(match[1]) * 1024 ** powers[match[2].toUpperCase()]);
}

export class AAScraper {
    static parseBooks($) {
        const books = [];
        const table = $("table")
            .filter((_, element) => {
            const header = $(element).find("tr").first().text();
            return header.includes("Author(s)") && header.includes("Mirrors");
        })
            .first();

        table.find("tr").slice(1).each((_, row) => {
            const cells = $(row).children("td");
            if (cells.length < 9)
                return;

            const md5 = cells
                .eq(8)
                .find('a[href*="md5="]')
                .first()
                .attr("href")
                ?.match(/[?&]md5=([a-f0-9]{32})/i)?.[1]
                .toLowerCase();
            const title = cells
                .eq(0)
                .find('a[href*="edition.php"]')
                .first()
                .text()
                .trim();
            if (!md5 || !title)
                return;

            const authorText = cells.eq(1).text().trim();
            const languageText = cells.eq(4).text().trim();
            const format = cells.eq(7).text().trim().toUpperCase();
            const yearText = cells.eq(3).text().trim();

            books.push({
                md5,
                title,
                authors: authorText
                    ? authorText.split(/\s*;\s*/).filter(Boolean)
                    : undefined,
                publisher: cells.eq(2).text().trim() || undefined,
                language: languageCodes[languageText] || languageText.toLowerCase() || undefined,
                format: format || undefined,
                size: sizeInBytes(cells.eq(6).text().trim()),
                year: /^\d{4}$/.test(yearText) ? Number(yearText) : undefined,
                source: "lgli",
            });
        });

        return books;
    }

    async scrapeUrl(url, page) {
        const crawlId = Math.random().toString(36).substring(7);
        logger.info(`[${crawlId}] Requesting search results...`);
        try {
            const response = await fetch(url, {
                headers: {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                    Accept: "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.5",
                },
                signal: AbortSignal.timeout(30000),
            });
            if (!response.ok)
                throw new Error(`Search source returned HTTP ${response.status}`);
            const $ = load(await response.text());
            const results = AAScraper.parseBooks($);
            logger.info(`[${crawlId}] Parsed ${results.length} books`);
            return {
                results,
                pagination: {
                    page,
                    per_page: results.length,
                    has_next: false,
                    has_previous: page > 1,
                    estimated_total_results: null,
                },
            };
        }
        catch (error) {
            logger.warn(`[${crawlId}] Search failed:`, error instanceof Error ? error.message : String(error));
            return {
                results: [],
                pagination: {
                    page,
                    per_page: 0,
                    has_next: false,
                    has_previous: page > 1,
                    estimated_total_results: null,
                },
            };
        }
    }

    async search(query) {
        const searchId = Math.random().toString(36).substring(7);
        const cached = await searchCacheManager.get(query);
        if (cached) {
            logger.info(`[${searchId}] Cache hit - returning ${cached.results.length} results`);
            return cached;
        }

        const result = await this.scrapeUrl(this.buildSearchUrl(query), query.page);
        result.results = result.results.filter((book) => {
            const extensionMatches = !query.ext?.length ||
                (book.format && query.ext.includes(book.format.toLowerCase()));
            const languageMatches = !query.lang?.length ||
                (book.language && query.lang.includes(book.language));
            return extensionMatches && languageMatches;
        });
        result.pagination.per_page = result.results.length;

        if (result.results.length > 0) {
            await searchCacheManager.set(query, result);
            logger.success(`[${searchId}] Found ${result.results.length} books`);
        }
        else {
            logger.warn(`[${searchId}] No results found`);
        }
        return result;
    }

    buildSearchUrl(query) {
        if (!BASE_URL)
            throw new Error("LG_BASE_URL is not configured");
        const params = new URLSearchParams({ req: query.q });
        if (query.page > 1)
            params.set("page", query.page.toString());
        return `${BASE_URL}/index.php?${params.toString()}`;
    }
}

export const aaScraper = new AAScraper();
