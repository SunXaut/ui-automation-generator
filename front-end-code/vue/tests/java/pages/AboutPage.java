// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * About 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class AboutPage {
    private final Page page;

    public AboutPage(Page page) {
        this.page = page;
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/about");
    }
}

// AUTO-GENERATED END