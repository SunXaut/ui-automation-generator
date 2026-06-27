// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Search 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class SearchPage {
    private final Page page;

    public SearchPage(Page page) {
        this.page = page;
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/search");
    }

    /**
     * 填写query
     */
    public void fillQuery(String value) {
        page.getByLabel("query").fill(value != null ? value : "test_value");
    }

    /**
     * 填写results
     */
    public void fillResults(String value) {
        page.getByLabel("results").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END