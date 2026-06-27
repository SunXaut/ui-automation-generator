// AUTO-GENERATED START
import com.microsoft.playwright.Page;
import pages.SearchPage;

/**
 * 搜索流程
 * 组合POM操作：goto → fillSearchInput → clickSearchButton
 */
public class SearchSearchBAW {
    private final SearchPage searchPage;

    public SearchSearchBAW(Page page) {
        this.searchPage = new SearchPage(page);
    }

    /**
     * 执行搜索流程
     */
    public void execute(String keyword) {
        // 1. goto
        searchPage.goto();
        // 2. fillSearchInput
        searchPage.fillSearchInput(keyword);
        // 3. clickSearchButton
        searchPage.clickSearchButton();
    }
}

// AUTO-GENERATED END