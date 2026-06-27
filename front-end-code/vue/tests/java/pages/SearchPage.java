// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Search 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class SearchPage {
    private final Page page;
    /** 输入搜索关键词 元素定位器 */
    private final Locator inputsearch关键词Input;

    public SearchPage(Page page) {
        this.page = page;
        this.inputsearch关键词Input = page.getByPlaceholder("输入搜索关键词");
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/search");
    }

    /**
     * 输入输入搜索关键词
     */
    public void fillInputsearch关键词input(String value) {
        this.inputsearch关键词Input.fill(value != null ? value : "test_value");
    }

    /**
     * 聚焦输入搜索关键词
     */
    public void focusInputsearch关键词input() {
        this.inputsearch关键词Input.focus();
    }

    /**
     * 失焦输入搜索关键词
     */
    public void blurInputsearch关键词input() {
        this.inputsearch关键词Input.blur();
    }

    /**
     * 填写searchQuery
     */
    public void fillSearchQuery(String value) {
        page.getByLabel("searchQuery").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END